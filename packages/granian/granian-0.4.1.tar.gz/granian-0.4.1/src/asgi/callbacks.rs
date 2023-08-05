use hyper::{Body, Request, Response};
use pyo3::prelude::*;
use pyo3_asyncio::TaskLocals;
use tokio::sync::oneshot;

use crate::{
    callbacks::{
        CallbackWrapper,
        callback_impl_run,
        callback_impl_loop_run,
        callback_impl_loop_step,
        callback_impl_loop_wake,
        callback_impl_loop_err
    },
    runtime::RuntimeRef,
    ws::{HyperWebsocket, UpgradeData}
};
use super::{
    io::{ASGIHTTPProtocol as HTTPProtocol, ASGIWebsocketProtocol as WebsocketProtocol},
    types::ASGIScope as Scope
};


#[pyclass]
pub(crate) struct CallbackRunnerHTTP {
    proto: Py<HTTPProtocol>,
    context: TaskLocals,
    cb: PyObject
}

impl CallbackRunnerHTTP {
    pub fn new(
        py: Python,
        cb: CallbackWrapper,
        proto: HTTPProtocol,
        scope: Scope
    ) -> Self {
        let pyproto = Py::new(py, proto).unwrap();
        Self {
            proto: pyproto.clone(),
            context: cb.context,
            cb: cb.callback.call1(py, (scope, pyproto)).unwrap()
        }
    }

    callback_impl_run!();
}

#[pymethods]
impl CallbackRunnerHTTP {
    fn _loop_task<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        CallbackTaskHTTP::new(py, self.cb.clone(), self.proto.clone(), self.context.clone())?.run(py)
    }
}

#[pyclass]
pub(crate) struct CallbackTaskHTTP {
    proto: Py<HTTPProtocol>,
    context: TaskLocals,
    cb: PyObject
}

impl CallbackTaskHTTP {
    pub fn new(
        py: Python,
        cb: PyObject,
        proto: Py<HTTPProtocol>,
        context: TaskLocals
    ) -> PyResult<Self> {
        Ok(Self { proto, context: context.copy_context(py)?, cb })
    }

    fn done(&self, py: Python) {
        if let Ok(mut proto) = self.proto.as_ref(py).try_borrow_mut() {
            if let Some(tx) = proto.tx() {
                let mut res = Response::new("Internal server error".into());
                *res.status_mut() = hyper::StatusCode::INTERNAL_SERVER_ERROR;
                let _ = tx.send(res);
            }
        }
    }

    fn err(&self, py: Python) {
        log::warn!("Application callable raised an exception");
        self.done(py)
    }

    callback_impl_loop_run!();
    callback_impl_loop_err!();
}

#[pymethods]
impl CallbackTaskHTTP {
    fn _loop_step(pyself: PyRef<'_, Self>, py: Python) -> PyResult<PyObject> {
        callback_impl_loop_step!(pyself, py)
    }

    fn _loop_wake(pyself: PyRef<'_, Self>, py: Python, fut: PyObject) -> PyResult<PyObject> {
        callback_impl_loop_wake!(pyself, py, fut)
    }
}

#[pyclass]
pub(crate) struct CallbackRunnerWebsocket {
    proto: Py<WebsocketProtocol>,
    context: TaskLocals,
    cb: PyObject
}

impl CallbackRunnerWebsocket {
    pub fn new(
        py: Python,
        cb: CallbackWrapper,
        proto: WebsocketProtocol,
        scope: Scope
    ) -> Self {
        let pyproto = Py::new(py, proto).unwrap();
        Self {
            proto: pyproto.clone(),
            context: cb.context,
            cb: cb.callback.call1(py, (scope, pyproto)).unwrap()
        }
    }

    callback_impl_run!();
}

#[pymethods]
impl CallbackRunnerWebsocket {
    fn _loop_task<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        CallbackTaskWebsocket::new(py, self.cb.clone(), self.proto.clone(), self.context.clone())?.run(py)
    }
}

#[pyclass]
pub(crate) struct CallbackTaskWebsocket {
    proto: Py<WebsocketProtocol>,
    context: TaskLocals,
    cb: PyObject
}

impl CallbackTaskWebsocket {
    pub fn new(
        py: Python,
        cb: PyObject,
        proto: Py<WebsocketProtocol>,
        context: TaskLocals
    ) -> PyResult<Self> {
        Ok(Self { proto, context: context.copy_context(py)?, cb })
    }

    fn done(&self, py: Python) {
        if let Ok(mut proto) = self.proto.as_ref(py).try_borrow_mut() {
            if let (Some(tx), res) = proto.tx() {
                let _ = tx.send(res);
            }
        }
    }

    fn err(&self, py: Python) {
        log::warn!("Application callable raised an exception");
        self.done(py)
    }

    callback_impl_loop_run!();
    callback_impl_loop_err!();
}

#[pymethods]
impl CallbackTaskWebsocket {
    fn _loop_step(pyself: PyRef<'_, Self>, py: Python) -> PyResult<PyObject> {
        callback_impl_loop_step!(pyself, py)
    }

    fn _loop_wake(pyself: PyRef<'_, Self>, py: Python, fut: PyObject) -> PyResult<PyObject> {
        callback_impl_loop_wake!(pyself, py, fut)
    }
}

// NOTE: we cannot use single `impl` function as structs with pyclass won't handle
//       dyn fields easily.
// pub(crate) async fn call(
//     cb: CallbackWrapper,
//     protocol: impl ASGIProtocol + IntoPy<PyObject>,
//     scope: Scope
// ) -> Result<(), ASGIFlowError> {
//     let (tx, rx) = oneshot::channel();
//     let callback = cb.callback.clone();
//     Python::with_gil(|py| {
//         callback.call1(py, (CallbackWatcher::new(py, cb, tx), scope, protocol))
//     })?;

//     match rx.await {
//         Ok(true) => Ok(()),
//         Ok(false) => {
//             log::warn!("Application callable raised an exception");
//             error_flow!()
//         },
//         _ => error_flow!()
//     }
// }

pub(crate) fn call_rtb_http(
    cb: CallbackWrapper,
    rt: RuntimeRef,
    req: Request<Body>,
    scope: Scope
) -> oneshot::Receiver<Response<Body>> {
    let (tx, rx) = oneshot::channel();
    let protocol = HTTPProtocol::new(rt, req, tx);

    Python::with_gil(|py| {
        let _ = CallbackRunnerHTTP::new(py, cb, protocol, scope).run(py);
    });

    rx
}

pub(crate) fn call_rtt_http(
    cb: CallbackWrapper,
    rt: RuntimeRef,
    req: Request<Body>,
    scope: Scope
) -> oneshot::Receiver<Response<Body>> {
    let (tx, rx) = oneshot::channel();
    let protocol = HTTPProtocol::new(rt, req, tx);

    tokio::task::spawn_blocking(move || {
        Python::with_gil(|py| {
            let _ = CallbackRunnerHTTP::new(py, cb, protocol, scope).run(py);
        });
    });

    rx
}

pub(crate) fn call_rtb_ws(
    cb: CallbackWrapper,
    rt: RuntimeRef,
    ws: HyperWebsocket,
    upgrade: UpgradeData,
    scope: Scope
) -> oneshot::Receiver<bool> {
    let (tx, rx) = oneshot::channel();
    let protocol = WebsocketProtocol::new(rt, tx, ws, upgrade);

    Python::with_gil(|py| {
        let _ = CallbackRunnerWebsocket::new(py, cb, protocol, scope).run(py);
    });

    rx
}

pub(crate) fn call_rtt_ws(
    cb: CallbackWrapper,
    rt: RuntimeRef,
    ws: HyperWebsocket,
    upgrade: UpgradeData,
    scope: Scope
) -> oneshot::Receiver<bool> {
    let (tx, rx) = oneshot::channel();
    let protocol = WebsocketProtocol::new(rt, tx, ws, upgrade);

    tokio::task::spawn_blocking(move || {
        Python::with_gil(|py| {
            let _ = CallbackRunnerWebsocket::new(py, cb, protocol, scope).run(py);
        });
    });

    rx
}

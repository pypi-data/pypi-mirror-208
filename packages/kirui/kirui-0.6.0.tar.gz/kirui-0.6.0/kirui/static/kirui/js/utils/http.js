
class Request {
    _on_complete(request, callback) {
        function complete(ev) {
            if (request.readyState !== 4) {
                return
            }

            document.querySelector('#loading').style.display = 'none'
            if (request.status === 340) {
                window.location.replace(request.getResponseHeader('Location'))
            } else if ([200, 201, 403].indexOf(request.status) > -1) {
                callback(request)
            }
        }

        return complete
    }

    _prepare() {
        document.querySelector('#loading').style.display = 'block'
    }

    post(url, data, callback) {
        this._prepare()
        let req = new XMLHttpRequest()
        req.open('POST', url)
        req.send(data)
        req.onreadystatechange = this._on_complete(req, callback)
    }

    get(url, callback) {
        this._prepare()
        let req = new XMLHttpRequest()
        req.open('GET', url)
        req.send()
        req.onreadystatechange = this._on_complete(req, callback)
    }
}

const request = new Request()

export { request }

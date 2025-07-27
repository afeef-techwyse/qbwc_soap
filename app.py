from flask import Flask, request, Response
from spyne import Application, rpc, ServiceBase, Unicode, Integer
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

class QBWebConnectorService(ServiceBase):
    @rpc(Unicode, Unicode, _returns=(Unicode, Integer))
    def authenticate(ctx, username, password):
        if username == "myusername" and password == "mypassword":
            return ["12345", 1]
        else:
            return ["", 0]

    @rpc(Unicode, _returns=Unicode)
    def sendRequestXML(ctx, ticket):
        return """<?xml version="1.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <CustomerQueryRq requestID="1">
      <MaxReturned>10</MaxReturned>
    </CustomerQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""

    @rpc(Unicode, Unicode, _returns=Integer)
    def receiveResponseXML(ctx, ticket, response):
        print("QB Response:", response)
        return 100

    @rpc(Unicode, _returns=Unicode)
    def getLastError(ctx, ticket):
        return "No error"

    @rpc(Unicode, _returns=Unicode)
    def closeConnection(ctx, ticket):
        return "Goodbye!"

soap_app = Application([QBWebConnectorService],
                       tns='qbwc.soap',
                       in_protocol=Soap11(validator='lxml'),
                       out_protocol=Soap11())

wsgi_app = WsgiApplication(soap_app)

app = Flask(__name__)

@app.route("/qbwc", methods=["POST"])
def soap_interface():
    def start_response(status, headers):
        response.status = status
        for key, value in headers:
            response.headers[key] = value
        return response.response.append

    response = Response()
    response.response = []
    response.headers = {}
    result = wsgi_app(request.environ, start_response)
    response.response.extend(result)
    return response

@app.route("/")
def index():
    return "QBWC SOAP App is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

import ssl
import paho.mqtt.client as mqtt

class K12MqttClient(mqtt.Client):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mqttHost = config['host']
        self.mqttPort = config['port']
        self.mqttKeepalive = config['keepalive']
        self.mqttTransport = config['transport']
        self.mqttusername = config['username']
        self.mqttpassword = config['password']
        self.mqttSubscribe = config['subscribe']

        self.tls_set(ca_certs=None, certfile=None, keyfile=None,
                     cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
        self.username_pw_set(self.mqttusername, password=self.mqttpassword)

    def run(self, on_connect, on_message):
        self.on_connect = on_connect
        self.on_message = on_message
        self.connect(self.mqttHost, self.mqttPort, self.mqttKeepalive)
        self.loop_forever()

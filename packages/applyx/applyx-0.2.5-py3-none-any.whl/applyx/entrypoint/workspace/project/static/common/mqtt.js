
class MQTT {

  constructor() {
    this.client = null
    this.config = null
    this.last = null
    this.reconnect = true
    this.log = false
    this.topics = {}
  }

  connect(url, options) {
    let self = this;

    Resource.load({
      modules: [
        'https://lf6-cdn-tos.bytecdntp.com/cdn/expire-1-M/mqtt/4.3.6/mqtt.min.js',
        'https://lf9-cdn-tos.bytecdntp.com/cdn/expire-1-M/pako/2.0.4/pako.min.js',
      ]
    }).ready((RESOURCE) => {
      self.client = mqtt.connect(url, options);
    });
  }

  subscribe(topic, options) {
    let self = this;
    if (!self.client || !self.client.connected) {
      return false;
    }
    self.client.subscribe(topic, options, (err, granted) => {
    });
    return true;
  }

  unsubscribe(topic, options) {
    let self = this;
    if (!self.client || !self.client.connected) {
      return false;
    }
    self.client.unsubscribe(topic, options, (err, granted) => {
    });
    return true;
  }

  publish(topic, message, options, callback) {
    let self = this;
    if (!self.client || !self.client.connected) {
      return false;
    }
    self.client.publish(topic, message, options, (err) => {
    });
    return true;
  }
}

window.MQTT = MQTT;

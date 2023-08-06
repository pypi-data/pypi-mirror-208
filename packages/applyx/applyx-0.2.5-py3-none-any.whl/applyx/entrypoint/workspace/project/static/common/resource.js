
class Resource {

  constructor(config) {
    this.config = config;
    this.templates = {};
  }

  static load(config) {
    return new Resource(config);
  }

  ready(callback) {
    let self = this;
    new Promise((resolve, reject) => {
      let promises = Array.from([
        self.load_stylesheets,
        self.load_scripts,
        self.load_modules,
        self.load_templates,
      ], (request) => new Promise((resolve, reject) => {
        request(self, resolve, reject);
      }));
      Promise.all(promises).then(() => {
        resolve();
      }).catch((error) => {
        reject(error);
      });
    }).then(() => {
      !!callback && callback(self);
    }).catch((error) => {
      console.log(error);
    });
  }

  load_modules(self, resolve, reject) {
    let promises = (self.config.modules || []).map(url => import(url));
    Promise.all(promises).then(() => {
      resolve();
    }).catch((error) => {
      reject(error);
    });
  }

  load_scripts(self, resolve, reject) {
    let scripts = {};
    (self.config.scripts || []).map(url => {
      if (/^\/static\//.test(url)) {
        url = window.location.origin + url;
      }
      let node = document.createElement('script');
      node.type = 'text/javascript';
      node.src = url;
      node.onload = node.onreadystatechange = function() {
        if (!this.readyState || this.readyState === 'loaded' || this.readyState === 'complete') {
          this.onload = this.onreadystatechange = null;
          scripts[this.src] = true;
        }
      };
      document.head.appendChild(node);
      scripts[url] = false;
    });
    self.poll_scripts(scripts, resolve);
  }

  poll_scripts(scripts, callback) {
    let self = this;
    let flags = [];
    for (let src in scripts) {
      flags.push(scripts[src])
    }

    if (flags.reduce((result, flag) => result && flag)) {
      callback();
    } else {
      setTimeout(() => {
        self.poll_scripts(scripts, callback);
      }, 10);
    }
  }

  load_stylesheets(self, resolve, reject) {
    let stylesheets = [];
    (self.config.stylesheets || []).map(url => {
      let node = document.createElement('link');
      node.type = 'text/css';
      node.rel = 'stylesheet';
      node.href = url;
      document.head.appendChild(node);
      stylesheets.push(node);
    });
    self.poll_stylesheets(stylesheets, resolve);
  }

  poll_stylesheets(stylesheets, callback) {
    let self = this;
    let flags = [];
    stylesheets.map((node) => {
      flags.push(!!node.sheet);
    });

    if (flags.reduce((result, flag) => result && flag)) {
      callback();
    } else {
      setTimeout(() => {
        self.poll_stylesheets(stylesheets, callback);
      }, 10);
    }
  }

  load_templates(self, resolve, reject) {
    let keys = [];
    let urls = [];
    Object.entries(self.config.templates || []).map((entry) => {
      keys.push(entry[0]);
      urls.push(entry[1]);
    });

    Promise.all(
      urls.map(url => fetch(url))
    ).then((requests) => Promise.all(
      requests.map((response) => response.text())
    )).then(results => {
      results.map((result, i) => {
        self.templates[keys[i]] = result;
      });
      resolve();
    }).catch((error) => {
      reject(error);
    });
  }
}

window.Resource = Resource;

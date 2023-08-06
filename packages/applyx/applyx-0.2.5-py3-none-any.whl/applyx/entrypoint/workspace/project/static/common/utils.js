
window.Utils = {
  orientation: {
    mode: {
      LANDSCAPE: {
        query: '(orientation: landscape)',
        txt: '橫屏',
      },
      PROTRAIT: {
        query: '(orientation: protrait)',
        txt: '竖屏',
      },
    },
    config(code) {
      let self = this;
      let mode = code == 'protrait' ? self.mode.PROTRAIT : self.mode.LANDSCAPE;
      let opposite_mode = code == 'protrait' ? self.mode.LANDSCAPE : self.mode.PROTRAIT;
      let mql = window.matchMedia(opposite_mode.query);
      if (mql.matches) {
        alert('请切换到' + mode.txt + '模式');
        return;
      }
      mql.addEventListener('change', (event) => {
        if (event.matches) {
          alert('请切换到' + mode.txt + '模式');
        }
      });
    }
  },

  date: {
    humanize(default_format, flag) {
      let gap = (Date.parse(new Date())-Date.parse(this))/1000;
      let text = '';
      if (gap < 60) {
        text = '刚刚';
      } else if (gap < 3600) {
        text =  Math.floor(gap/60).toString() + '分钟前';
      } else if (gap < 86400) {
        text = Math.floor(gap/3600).toString() + '小时前';
      } else if (gap < 86400 * 2) {
        text = '昨天';
      } else if (gap < 86400 * 3) {
        text = '前天';
      } else if (flag) {
        text = moment(this).format(default_format || 'YYYY-MM-DD');
      } else if (gap < 86400 * 30) {
        text = Math.floor(gap/86400).toString() + '天前';
      } else if (gap < 86400 * 30 * 6) {
        text = Math.floor(gap/86400/30).toString() + '个月前';
      } else {
        text = moment(this).format(default_format || 'YYYY-MM-DD');
      }
      return text;
    },
  },

  video: {
    duration(seconds) {
      let hour = Math.floor(seconds/3600);
      let minute = Math.floor((seconds % 3600) / 60);
      let second = seconds % 60;
      let duration_str = '';
      duration_str += (hour > 0 ? hour.toString() + ':' : '');
      duration_str += (minute < 10 ? '0' : '') + minute.toString() + ':';
      duration_str += (second < 10 ? '0' : '') + second.toString();
      return duration_str;
    }
  },
}

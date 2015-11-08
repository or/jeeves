'use strict';

function update_progress_bars() {
  var pbars;
  pbars = $('.build-progress');

  pbars.each(function (index) {
    var pbar = $(this);
    if (pbar.data('initial-timestamp') == null) {
      pbar.data('initial-timestamp', $.now() / 1000);
    } else {
      return;
    }

    React.render(React.createElement(ProgressBar, { initial_timestamp: pbar.data('initial-timestamp'),
      initial_elapsed_time: pbar.data('initial-elapsed-time'),
      estimated_time: pbar.data('estimated-time') }), pbar.get()[0]);
  });
}

function update_age_displays() {
  var ages;
  ages = $('.age-display');

  ages.each(function (index) {
    var age_element = $(this);
    if (age_element.data('initial-timestamp') == null) {
      age_element.data('initial-timestamp', $.now() / 1000);
    } else {
      return;
    }

    React.render(React.createElement(AgeDisplay, { initial_timestamp: age_element.data('initial-timestamp'),
      initial_age: age_element.data('initial-age') }), age_element.get()[0]);
  });
}

var ProgressBar = React.createClass({
  displayName: 'ProgressBar',

  getInitialState: function getInitialState() {
    return {
      now: $.now() / 1000
    };
  },

  render: function render() {
    setTimeout((function () {
      this.setState({ now: $.now() / 1000 });
    }).bind(this), 1000);

    var start_time = this.props.initial_timestamp - this.props.initial_elapsed_time;
    var end_time = start_time + this.props.estimated_time;

    var elapsed_time = this.state.now - start_time;
    var elapsed_time_string = get_exact_time_difference_string(elapsed_time);

    var normal_percentage;
    var overtime_percentage;
    var overtime = false;

    if (this.props.estimated_time == null) {
      normal_percentage = 100.0 * (1.0 - Math.exp(-elapsed_time / 300.0));
    } else {
      if (elapsed_time > this.props.estimated_time) {
        overtime = true;
        var over = elapsed_time - this.props.estimated_time;
        var estimation_steps = Math.max(this.props.estimated_time / 10, 10);
        var projected_eta = (Math.floor(over / estimation_steps) + 1) * estimation_steps + this.props.estimated_time;

        normal_percentage = 100.0 * this.props.estimated_time / projected_eta;
        overtime_percentage = 100.0 * over / projected_eta;
      } else {
        normal_percentage = 100.0 * elapsed_time / this.props.estimated_time;
      }
    }

    var overtime_bar;
    if (overtime) {
      overtime_bar = React.createElement('div', {
        className: 'progress-bar progress-bar-warning progress-bar-striped',
        style: { width: overtime_percentage + "%" } });
    }

    return React.createElement(
      'div',
      { className: 'progress' },
      React.createElement(
        'div',
        { className: "progress-bar progress-bar-success" + (!overtime ? " progress-bar-striped" : ""),
          style: { width: normal_percentage + "%" }
        },
        React.createElement(
          'span',
          null,
          elapsed_time_string
        )
      ),
      overtime_bar
    );
  }
});

var AgeDisplay = React.createClass({
  displayName: 'AgeDisplay',

  getInitialState: function getInitialState() {
    return {
      now: $.now() / 1000
    };
  },

  render: function render() {
    var start_time = this.props.initial_timestamp - this.props.initial_age;
    var num_seconds = this.state.now - start_time;

    var age = get_rough_time_difference_string(num_seconds);

    setTimeout((function () {
      this.setState({ now: $.now() / 1000 });
    }).bind(this), age.time_til_change * 1000);

    return React.createElement(
      'span',
      null,
      age.value,
      ' ago'
    );
  }
});

var LogLine = React.createClass({
  displayName: 'LogLine',

  render: function render() {
    var extraClassName = '';
    if (this.props.stderr) {
      extraClassName += ' stderr';
    }

    return React.createElement(
      'tr',
      null,
      React.createElement(
        'td',
        { className: "log-line-number noselect" + extraClassName },
        this.props.line_number
      ),
      React.createElement(
        'td',
        { className: "log-line-data" + extraClassName },
        this.props.data
      )
    );
  }
});

var Log = React.createClass({
  displayName: 'Log',

  getInitialState: function getInitialState() {
    return {
      data: this.props.data
    };
  },

  render: function render() {
    var lines = [];
    var raw_lines = this.props.data.split('\n');
    var i;
    for (i = 0; i < raw_lines.length; ++i) {
      var raw_line = raw_lines[i];
      var line = raw_line;
      var stderr = false;
      if (line.startsWith('__stderr:')) {
        line = line.substring('__stderr: '.length);
        stderr = true;
      }
      lines.push({ number: i + 1, data: line, stderr: stderr });
    }

    var style = this.props.style;
    style.background = '#000';
    style.overflowY = 'auto';

    return React.createElement(
      'div',
      { style: style },
      React.createElement(
        'table',
        { style: { width: '100%' } },
        lines.map(function (line) {
          return React.createElement(LogLine, { line_number: line.number, data: line.data, stderr: line.stderr });
        })
      )
    );
  }
});

var LogView = React.createClass({
  displayName: 'LogView',

  getInitialState: function getInitialState() {
    var active_log = null;
    if (this.props.log_data.jobs.length > 0) {
      active_log = this.props.log_data.jobs[this.props.log_data.jobs.length - 1];
    }

    return {
      log_data: this.props.log_data,
      active_log: active_log
    };
  },

  setLogData: function setLogData(log_data) {
    var active_log = this.state.active_log;
    if (active_log == null && log_data.jobs.length > 0) {
      active_log = this.props.log_data.jobs[this.props.log_data.jobs.length - 1];
    }

    this.setState({
      log_data: log_data,
      active_log: active_log
    });

    setTimeout(this.autoScroll, 0);
  },

  clickJobTab: function clickJobTab(event) {
    event.preventDefault();
    var active_log = $(event.target).data('job');
    this.setState({
      log_data: this.props.log_data,
      active_log: active_log
    });
  },

  autoScroll: function autoScroll() {
    var auto_scrolling = $(this.refs.auto_scrolling.getDOMNode());
    if (!auto_scrolling.prop('checked') || this.state.active_log == null) {
      return;
    }

    var page = $(document.body);
    page.animate({
      scrollTop: page.prop('scrollHeight')
    }, 500);
  },

  render: function render() {
    return React.createElement(
      'div',
      null,
      React.createElement(
        'nav',
        { className: 'navbar navbar-default', style: { marginBottom: '0', borderRadius: '0' } },
        React.createElement(
          'div',
          { className: 'container-fluid' },
          React.createElement(
            'div',
            { className: 'navbar-header' },
            React.createElement(
              'button',
              { type: 'button', className: 'navbar-toggle collapsed',
                'data-toggle': 'collapse', 'data-target': '#log-navbar-collapse',
                'aria-expanded': 'false' },
              React.createElement('span', { className: 'fa fa-bars' })
            ),
            React.createElement(
              'span',
              { className: 'navbar-brand' },
              'Logs'
            )
          ),
          React.createElement(
            'div',
            { className: 'collapse navbar-collapse', id: 'log-navbar-collapse',
              style: { overflowY: 'hidden' } },
            React.createElement(
              'ul',
              { className: 'nav navbar-nav', style: { marginLeft: '1em' } },
              this.state.log_data.jobs.map((function (name) {
                if (this.state.active_log == name) {
                  var className = "active";
                }
                return React.createElement(
                  'li',
                  { key: name,
                    role: 'presentation', className: className },
                  React.createElement(
                    'a',
                    { href: '#', onClick: this.clickJobTab, 'data-job': name },
                    name
                  )
                );
              }).bind(this))
            ),
            React.createElement(
              'div',
              { className: 'nav navbar-nav navbar-right', style: { paddingLeft: '40px' } },
              React.createElement(
                'label',
                { className: 'checkbox' },
                React.createElement('input', { id: 'test-stuff', type: 'checkbox', ref: 'auto_scrolling', defaultChecked: true }),
                React.createElement(
                  'span',
                  { style: { fontWeight: 'normal', marginLeft: '0.5em' } },
                  'Auto scroll'
                )
              )
            )
          )
        )
      ),
      this.state.log_data.jobs.map((function (name) {
        var display = 'none';
        if (name == this.state.active_log) {
          display = 'block';
        }
        return React.createElement(Log, { key: name, ref: "ref_" + name,
          data: this.state.log_data.data[name],
          style: { display: display } });
      }).bind(this))
    );
  }
});


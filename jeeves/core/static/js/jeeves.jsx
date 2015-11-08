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

    React.render(
      <ProgressBar initial_timestamp={pbar.data('initial-timestamp')}
                   initial_elapsed_time={pbar.data('initial-elapsed-time')}
                   estimated_time={pbar.data('estimated-time')}/>,
      pbar.get()[0]
    );
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

    React.render(
      <AgeDisplay initial_timestamp={age_element.data('initial-timestamp')}
                  initial_age={age_element.data('initial-age')}/>,
      age_element.get()[0]
    );
  });
}

var ProgressBar = React.createClass({
  getInitialState() {
    return {
      now: $.now() / 1000,
    }
  },

  render() {
    setTimeout((function() {
      this.setState({now: $.now() / 1000});
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
        var estimation_steps = Math.max(this.props.estimated_time / 10, 10)
        var projected_eta = (Math.floor(over / estimation_steps) + 1) * estimation_steps + this.props.estimated_time;

        normal_percentage = 100.0 * this.props.estimated_time / projected_eta;
        overtime_percentage = 100.0 * over / projected_eta;
      } else {
        normal_percentage = 100.0 * elapsed_time / this.props.estimated_time;
      }
    }

    var overtime_bar;
    if (overtime) {
      overtime_bar = <div
          className="progress-bar progress-bar-warning progress-bar-striped"
          style={{width: overtime_percentage + "%" }} />;
    }

    return (
      <div className="progress">
        <div className={
              "progress-bar progress-bar-success" +
                (!overtime ? " progress-bar-striped" : "")
             }
             style={{width: normal_percentage + "%" }}
             ><span>{elapsed_time_string}</span></div>
        {overtime_bar}
      </div>
    );
  }
});


var AgeDisplay = React.createClass({
  getInitialState() {
    return {
      now: $.now() / 1000,
    }
  },

  render() {
    var start_time = this.props.initial_timestamp - this.props.initial_age;
    var num_seconds = this.state.now - start_time;

    var age = get_rough_time_difference_string(num_seconds);

    setTimeout((function() {
      this.setState({now: $.now() / 1000});
    }).bind(this), age.time_til_change * 1000);

    return (
      <span>{age.value} ago</span>
    );
  }
});


var LogLine = React.createClass({
  render() {
    var extraClassName = '';
    if (this.props.stderr) {
      extraClassName += ' stderr';
    }

    return (
      <tr>
        <td className={"log-line-number noselect" + extraClassName}>
          {this.props.line_number}
        </td>
        <td className={"log-line-data" + extraClassName}>
          {this.props.data}
        </td>
      </tr>
    );
  }
});


var Log = React.createClass({
  getInitialState() {
    return {
      data: this.props.data,
    };
  },

  render() {
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
      lines.push({number: i + 1, data: line, stderr: stderr});
    }

    var style = this.props.style;
    style.height = '400px';
    style.background = '#000';
    style.overflowY = 'auto';

    return (
      <div style={style}>
        <table style={{width: '100%'}}>
          {lines.map(function(line) {
            return <LogLine line_number={line.number} data={line.data} stderr={line.stderr}/>
          })}
        </table>
      </div>
    );
  }
});


var LogView = React.createClass({
  getInitialState() {
    var active_log = null;
    if (this.props.log_data.jobs.length > 0) {
      active_log = this.props.log_data.jobs[this.props.log_data.jobs.length - 1];
    }

    return {
      log_data: this.props.log_data,
      active_log: active_log,
    }
  },

  setLogData(log_data) {
    var active_log = this.state.active_log;
    if (active_log == null && log_data.jobs.length > 0) {
      active_log = this.props.log_data.jobs[this.props.log_data.jobs.length - 1];
    }

    this.setState({
      log_data: log_data,
      active_log: active_log,
    });

    setTimeout(this.autoScroll, 0);
  },

  clickJobTab(event) {
    event.preventDefault();
    var active_log = $(event.target).data('job');
    this.setState({
      log_data: this.props.log_data,
      active_log: active_log,
    });
  },

  autoScroll() {
    var auto_scrolling = $(this.refs.auto_scrolling.getDOMNode());
    if (!auto_scrolling.prop('checked') ||
        this.state.active_log == null) {
      return;
    }

    var i;
    for (i = 0; i < this.props.log_data.jobs.length; ++i) {
      var name = this.props.log_data.jobs[i];
      var log = $(this.refs['ref_' + name].getDOMNode());
      log.animate({
        scrollTop: log.prop('scrollHeight')
      }, 500);
    }
  },

  render() {
    return (
      <div>
        <nav className="navbar navbar-default" style={{marginBottom: '0', borderRadius: '0'}}>
          <div className="container-fluid">
            <div className="navbar-header">
              <button type="button" className="navbar-toggle collapsed"
                      data-toggle="collapse" data-target="#log-navbar-collapse"
                      aria-expanded="false">
                <span className="fa fa-bars"></span>
              </button>
              <span className="navbar-brand">Logs</span>
            </div>

            <div className="collapse navbar-collapse" id="log-navbar-collapse"
                 style={{overflowY: 'hidden'}}>
              <ul className="nav navbar-nav" style={{marginLeft: '1em'}}>
                {this.state.log_data.jobs.map(function(name) {
                  if (this.state.active_log == name) {
                    var className="active";
                  }
                  return (
                    <li key={name}
                        role="presentation" className={className}>
                      <a href="#" onClick={this.clickJobTab} data-job={name}>{name}</a>
                    </li>
                  );
                }.bind(this))}
              </ul>

              <div className="nav navbar-nav navbar-right" style={{paddingLeft: '40px'}}>
                <label className="checkbox">
                  <input id="test-stuff" type="checkbox" ref="auto_scrolling" defaultChecked={true}/>
                  <span style={{fontWeight: 'normal', marginLeft: '0.5em'}}>Auto scroll</span>
                </label>
              </div>
            </div>
          </div>
        </nav>
        {this.state.log_data.jobs.map(function(name) {
          var display = 'none';
          if (name == this.state.active_log) {
            display = 'block';
          }
          return (
            <Log key={name} ref={"ref_" + name}
                 data={this.state.log_data.data[name]}
                 style={{display: display}}/>
          );
        }.bind(this))}
      </div>
    );
  }
});

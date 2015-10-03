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


var Log = React.createClass({
  getInitialState() {
    return {
      data: this.props.data,
    };
  },

  render() {
    return (
      <div style={this.props.style}>
        <pre className="log-data">{
          this.state.data
        }</pre>
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
  },

  clickJobTab(event) {
    event.preventDefault();
    var active_log = $(event.target).data('job');
    this.setState({
      log_data: this.props.log_data,
      active_log: active_log,
    });
  },

  render() {
    return (
      <div>
        <nav className="navbar navbar-default" style={{marginBottom: '0'}}>
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
                 style={{marginTop: '10px', overflowY: 'hidden'}}>
              <ul className="navbar-nav nav nav-tabs"
                  style={{border: '0', marginLeft: '1em', marginBottom: '0'}}>
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

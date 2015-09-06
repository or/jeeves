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
      React.createElement(ProgressBar, {
        initial_timestamp: pbar.data('initial-timestamp'),
        initial_elapsed_time: pbar.data('initial-elapsed-time'),
        estimated_time: pbar.data('estimated-time'),
      }),
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
      React.createElement(AgeDisplay, {
        initial_timestamp: age_element.data('initial-timestamp'),
        initial_age: age_element.data('initial-age'),
      }),
      age_element.get()[0]
    );
  });
}

ProgressBar = React.createClass({
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


AgeDisplay = React.createClass({
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

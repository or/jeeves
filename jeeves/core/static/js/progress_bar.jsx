function get_time_difference_string(num_seconds) {
  var mins = Math.floor(num_seconds / 60);
  var secs = Math.floor(num_seconds - mins * 60);

  var result = '';
  if (secs > 0) {
    result += secs + ' sec';
    if (secs != 1) {
      result += 's';
    }
  }

  if (mins > 0) {
    var part = mins + ' min';
    if (mins != 1) {
      part += 's';
    }
    if (result != '') {
      result = part + ', ' + result;
    }
  }

  if (result == '') {
    result = '0 secs';
  }

  return result;
}

function update_progress_bars() {
  var pbars = $('.build-progress');

  pbars.each(function (index) {
    var pbar = $(this);
    if (pbar.data('initial-timestamp') == null) {
      pbar.data('initial-timestamp', $.now() / 1000);
    }

    var initial_timestamp = pbar.data('initial-timestamp');
    var initial_elapsed_time = pbar.data('initial-elapsed-time');
    var estimated_time = pbar.data('estimated-time');

    var start_time = initial_timestamp - initial_elapsed_time;
    var end_time = start_time + estimated_time;
    var now = $.now() / 1000;

    var elapsed_time = now - start_time;
    var elapsed_time_string = get_time_difference_string(elapsed_time);

    var normal_percentage;
    var overtime_percentage;
    var overtime = false;

    if (estimated_time == null) {
      normal_percentage = 100.0 * (1.0 - Math.exp(-elapsed_time / 300.0));
    } else {
      if (elapsed_time > estimated_time) {
        overtime = true;
        var over = elapsed_time - estimated_time;
        var estimation_steps = Math.max(estimated_time / 10, 10)
        var projected_eta = (Math.floor(over / estimation_steps) + 1) * estimation_steps + estimated_time;

        normal_percentage = 100.0 * estimated_time / projected_eta;
        overtime_percentage = 100.0 * over / projected_eta;
      } else {
        normal_percentage = 100.0 * elapsed_time / estimated_time;
      }
    }

    React.render(
      React.createElement(ProgressBar, {
        'id': pbar.prop('id'),
        'data_estimated_time': estimated_time,
        'data_initial_timestamp': initial_timestamp,
        'data_initial_elapsed_time': initial_elapsed_time,
        'duration': elapsed_time_string,
        'overtime': overtime,
        'normal_percentage': normal_percentage,
        'overtime_percentage': overtime_percentage,
      }),
      pbar.get()[0]
    );
  });

  setTimeout(update_progress_bars, 5000);
}


ProgressBar = React.createClass({
  render() {
    var overtime_bar;
    if (this.props.overtime) {
      overtime_bar = <div
          className="progress-bar progress-bar-warning active progress-bar-striped"
          style={{width: this.props.overtime_percentage + "%" }} />;
    }

    return (
      <div id={this.props.id }
           className="progress"
           data-initial-elapsed-time={this.props.data_initial_elapsed_time}
           data-estimated-time={this.props.data_estimated_time}>
        <div className={
              "progress-bar progress-bar-success" +
                (!this.props.overtime ? " active progress-bar-striped" : "")
             }
             style={{width: this.props.normal_percentage + "%" }}
             ><span>{this.props.duration}</span></div>
        {overtime_bar}
      </div>
    );
  }
});

function get_exact_time_difference_string(num_seconds) {
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
    } else {
      result = part;
    }
  }

  if (result == '') {
    result = '0 secs';
  }

  return result;
}


function get_rough_time_difference_string(num_seconds) {
  if (num_seconds < 60) {
    return {value: "moments", time_til_change: 60 - num_seconds + 1};
  }

  units = [
    ['year', 60 * 60 * 24 * 365.2425],
    ['month', 60 * 60 * 24 * 30.5],
    ['week', 60 * 60 * 24 * 7],
    ['day', 60 * 60 * 24],
    ['hour', 60 * 60],
    ['min', 60],
    ['sec', 1],
  ]

  var result;
  var time_til_change;
  for (i = 0; i < units.length; ++i) {
    var unit = units[i][0];
    var duration = units[i][1];
    number = Math.floor(num_seconds / duration);
    if (number > 0 || duration == 1) {
      result = '' + number + ' ' + unit;
      if (number != 1) {
        result += 's';
      }
      if (duration == 1) {
        time_til_change = 1;
      } else {
        // calculate the timespan til the next number at this duration,
        // give 1 extra second, to make sure it'll result in a switch
        time_til_change = (number + 1) * duration - num_seconds + 1;
      }
      break;
    }
  }

  return {value: result, time_til_change: time_til_change}
}


function do_action(url) {
  $.ajax({
    url: url,

    dataType: 'json',

    success: function (data) {
      $('#messages').replaceWith(data.messages_html);
    },

    error: function (data) {
      $('#messages').html('<div role="alert" class="alert alert-danger">An error occurred.</div>');
    }
  });
}

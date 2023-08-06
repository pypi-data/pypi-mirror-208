#%%
"""Datetime-related utilities"""
# from datetime import datetime
import datetime
import math
import re

def get_current_timestamp():
    """Get current timestamp
    current_timestamp: Timestamp object - Used for difference calcs
    filename_timestamp: 'YYYY-MM-DD_HHMMSS' - Used for filenames
    log_timestamp: 'YYYY-MM-DD HH:MM:SS' - Used for logs"""
    
    current_timestamp = datetime.datetime.now()

    filename_timestamp = (
        datetime.datetime
        .fromtimestamp(datetime.datetime.now().timestamp())
        .strftime("%Y-%m-%d_%H%M%S")
        )
    
    log_timestamp = (
        datetime.datetime
        .fromtimestamp(datetime.datetime.now().timestamp())
        .strftime("%Y-%m-%d %H:%M:%S")
        )
                         
    return [current_timestamp, filename_timestamp, log_timestamp]

def get_duration(then, now=datetime.datetime.now()):#, interval = "default"):
    """Return the duration between two timestamps"""
    # Returns a duration as specified by variable interval
    # Functions, except totalDuration, returns [quotient, remainder]

    duration = now - then # For build-in functions
    duration_in_s = duration.total_seconds() 
    
    def get_years():
      return divmod(duration_in_s, 31536000) # Seconds in a year=31536000.

    def get_days(seconds = None):
      return divmod(seconds if seconds != None else duration_in_s, 86400) # Seconds in a day = 86400

    def get_hours(seconds = None):
      return divmod(seconds if seconds != None else duration_in_s, 3600) # Seconds in an hour = 3600

    def get_minutes(seconds = None):
      return divmod(seconds if seconds != None else duration_in_s, 60) # Seconds in a minute = 60

    def get_seconds(seconds = None):
      if seconds != None:
        return divmod(seconds, 1)   
      return duration_in_s

    def total_duration():
        years_list = get_years()
        days_list = get_days(years_list[1]) # Use remainder to calculate next variable
        hours_list = get_hours(days_list[1])
        mins_list = get_minutes(hours_list[1])
        secs_list = get_seconds(mins_list[1])

        return_string = ''

        if int(days_list[0]) > 0:
            return_string += f'{int(days_list[0])} days, '

        if int(hours_list[0]) > 0:
            return_string += f'{int(hours_list[0])} hours, '

        if int(mins_list[0]) > 0:
            return_string += f'{int(mins_list[0])} minutes, '

        return_string += f'{math.ceil(int(secs_list[0]))} seconds'
        
        #return "Time between dates: {} days, {} hours, {} minutes and {} seconds".format(int(d[0]), int(h[0]), int(m[0]), int(s[0]))
        return return_string

    days_between = int(get_days()[0])
    hours_between = int(get_hours()[0])
    minutes_between = int(get_minutes()[0])
    seconds_between = int(get_seconds())
    duration_string = total_duration()
    
    return (
        days_between,
        hours_between,
        minutes_between,
        seconds_between,
        duration_string
    )

def determine_date_format(date_list):
  """Takes a list of dates and attempts to determine their format"""

  def is_definitely_year(segment):
      """Checks if a segment is definitely a year"""
      for segment_value in segment:
          if len(segment_value) == 4 and segment_value.isdigit():
              return True
      return False

  def value_above_twelve(segment):
      """Checks if a segment has a value > 12"""
      has_any_value_gt_12 = any(int(segment_value) > 12 for segment_value in segment)
      return has_any_value_gt_12

  def estimate_day_and_month(list1, list2):
      """Estimates the positions of day and month based on the number of unique values in two lists"""
      unique_values_list1 = len(set(list1))
      unique_values_list2 = len(set(list2))

      if (unique_values_list1 == 1 and unique_values_list2 >= 2) or (unique_values_list1 >= 2 and unique_values_list2 >= 10):
          return ['M', 'D']
      elif (unique_values_list2 == 1 and unique_values_list1 >= 2) or (unique_values_list2 >= 2 and unique_values_list1 >= 10):
          return ['D', 'M']
      else:
          return []
  
  def analyze_year_beginning(date_list):
      """Analyzes the likely beginning positions of the year in date_list"""
      combinations_12 = set(date[:2] for date in date_list)
      combinations_56 = set(date[4:6] for date in date_list)

      combinations_12_bool = all(combination in {"19", "20"} for combination in combinations_12)
      combinations_56_bool = all(combination in {"19", "20"} for combination in combinations_56)

      if combinations_12_bool and not combinations_56_bool:
         return 'first4'

      if combinations_56_bool and not combinations_12_bool:
         return 'last4'
      
      return None
  
  segment1 = []
  segment2 = []
  segment3 = []
  delimiter = []
  date_format_list = ['', '', '']
  date_format = ''

  # Remove rows without at least 4 digits
  date_list = [date for date in date_list if sum(c.isdigit() for c in date) >= 4]

  # Remove duplicates while preserving the order
  date_list = list(dict.fromkeys(date_list))

  # Logic if delimiter present
  if any(elem in date_list[0] for elem in ['-', '/']):
    # Extract date portion from each string using regex pattern
    date_pattern = r"(\d{1,4})([-/]?)(\d{1,4})([-/]?)(\d{1,4})"
    for date in date_list:
        match = re.search(date_pattern, date)
        if match:
            groups = match.groups()
            segment1.append(groups[0])
            segment2.append(groups[2])
            segment3.append(groups[4])
            delimiter.append(groups[1])

    # Get unique values of each segment
    segment1 = list(dict.fromkeys(segment1))
    segment2 = list(dict.fromkeys(segment2))
    segment3 = list(dict.fromkeys(segment3))
  
  # 8 digit dates with no delimiter
  elif all(len(date) == 8 and date.isdigit() for date in date_list):
    year_position = analyze_year_beginning(date_list)
    
    if year_position:
      if year_position == 'first4':
        segment1 = [date[:4] for date in date_list]
        segment2 = [date[4:6] for date in date_list]
        segment3 = [date[6:8] for date in date_list]
        delimiter = ['']

        # Get unique values of each segment
        segment1 = list(dict.fromkeys(segment1))
        segment2 = list(dict.fromkeys(segment2))
        segment3 = list(dict.fromkeys(segment3))
        
      if year_position == 'last4':
        segment1 = [date[:2] for date in date_list]
        segment2 = [date[2:4] for date in date_list]
        segment3 = [date[4:8] for date in date_list]
        delimiter = ['']

        # Get unique values of each segment
        segment1 = list(dict.fromkeys(segment1))
        segment2 = list(dict.fromkeys(segment2))
        segment3 = list(dict.fromkeys(segment3))

  if segment1:
    # Check if the first segment is definitely a year
    first_segment_year = is_definitely_year(segment1)
    if first_segment_year:
        date_format_list[0] = 'Y'

    if 'Y' not in date_format_list:
        # Check if the third segment is definitely a year
        third_segment_year = is_definitely_year(segment3)
        if third_segment_year:
            date_format_list[2] = 'Y'

    # Check if the first segment is definitely a day
    if 'Y' in date_format_list and date_format_list[0] != 'Y':
      first_segment_day = value_above_twelve(segment1)
      if first_segment_day:
          date_format_list[0] = 'D'

    # Check if the second segment is definitely a day
    second_segment_day = value_above_twelve(segment2)
    if second_segment_day:
        date_format_list[1] = 'D'

    # Check if the third segment is definitely a day
    if 'Y' in date_format_list and 'D' not in date_format_list and date_format_list[2] != 'Y':
      third_segment_day = value_above_twelve(segment3)
      if third_segment_day:
          date_format_list[2] = 'D'

    # Check if the first segment is definitely a year
    if 'D' in date_format_list and 'Y' not in date_format_list and date_format_list[0] != 'D':
      first_segment_year = value_above_twelve(segment1)
      if first_segment_year:
          date_format_list[0] = 'Y'

    # Check if the third segment is definitely a year
    if 'D' in date_format_list and 'Y' not in date_format_list and date_format_list[2] != 'D':
      third_segment_year = value_above_twelve(segment3)
      if third_segment_year:
          date_format_list[2] = 'Y'

    # Assign 'M' to the position that is still empty
    if 'Y' in date_format_list and 'D' in date_format_list:
      for i in range(len(date_format_list)):
          if date_format_list[i] == '':
              date_format_list[i] = 'M'
              break

    if date_format_list == ['', '', 'Y']:
        remaining_values = estimate_day_and_month(segment1, segment2)
        if remaining_values:
          date_format_list[0] = remaining_values[0]
          date_format_list[1] = remaining_values[1]
    elif date_format_list == ['Y', '', '']:
        remaining_values = estimate_day_and_month(segment2, segment3)
        if remaining_values:
          date_format_list[1] = remaining_values[0]
          date_format_list[2] = remaining_values[1]
    
    if '' not in date_format_list:
      # Build date_format string based on segment lengths
      for i, segment in enumerate([segment1, segment2, segment3]):
          max_length = max(len(value) for value in segment)
          if date_format_list[i] == 'Y':
              date_format += 'Y' * max_length
          elif date_format_list[i] == 'M':
              date_format += 'M' * max_length
          elif date_format_list[i] == 'D':
              date_format += 'D' * max_length
          if i != 2:
              date_format += delimiter[0]
    else:
        date_format = None
  else:
      date_format = None

  # Confirm determined pattern works before returning
  if date_format:
    try:
      format_string = date_format.replace('DD', '%d').replace('D', '%d').replace('MM', '%m').replace('M', '%m').replace('YYYY', '%Y').replace('YY', '%Y')
      validated_dates = [datetime.datetime.strptime(date_string, format_string).date() for date_string in date_list]
    except ValueError:
      date_format = None
  
  return date_format, format_string

#%%
# Left in for testing purposes
# if __name__ == "__main__":
"""
import pandas as pd

file_path = r''

if file_path:
  # Read the .txt file into a DataFrame
  df = pd.read_csv(file_path, delimiter='\t', encoding='utf-16')

  date_list = df['DownloadDatePST'].tolist()
#%%
determine_date_format(date_list)

#%%

date_list = ['13/5/2023', '5/5/2023', '17/10/2023']
determine_date_format(date_list)

#%%

date_list = ['5/5/2023', '6/5/2023', '7/5/2023']
determine_date_format(date_list)

#%%

date_list = ['5/5/2023', '5/6/2023', '5/7/2023']
determine_date_format(date_list)

#%%

date_list = ['2023-5-5', '2023-5-6', '2023-5-17']
determine_date_format(date_list)

#%%

date_list = ['2023-5-15', '2023-5-16', '2023-5-17']
determine_date_format(date_list)

#%%

date_list = ['20230515', '20230516', '20230517']
determine_date_format(date_list)

#%%

date_list = ['05152023', '05162023', '05172023']
determine_date_format(date_list)

#%%

date_list = ['051523', '051623', '051723']
print(determine_date_format(date_list))

#%%

date_list = ['05052023', '05052023', '05052023']
print(determine_date_format(date_list))

#%%
"""
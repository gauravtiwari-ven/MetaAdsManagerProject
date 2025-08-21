from datetime import datetime, timedelta

class Stripper():
    def __init__(self, start_date_str, end_date_str):
        self.start_date_str = start_date_str
        self.end_date_str = end_date_str
        print('Date Strings are \n')
        print('Date Strings are \n',start_date_str)
        print('Date Strings are \n',end_date_str)

    def get_formatted_dates(self):
        # Convert start and end date strings to datetime objects
        start_date = None
        end_date = None
        
        # Check for NaN or empty values
        if str(self.start_date_str) != "nan" and str(self.start_date_str) != "" and self.start_date_str is not None:
            try:
                # Try multiple date formats
                date_formats = ['%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%y', '%d/%m/%y']
                start_date = None
                for fmt in date_formats:
                    try:
                        start_date = datetime.strptime(str(self.start_date_str), fmt)
                        break
                    except ValueError:
                        continue
                
                if start_date is None:
                    print(f"Invalid start_date format: {self.start_date_str}")
                    return None, None
            except Exception as e:
                print(f"Error parsing start_date: {e}")
                return None, None
         
        if str(self.end_date_str) != "nan" and str(self.end_date_str) != "" and self.end_date_str is not None:
            try:
                # Try multiple date formats
                date_formats = ['%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%y', '%d/%m/%y']
                end_date = None
                for fmt in date_formats:
                    try:
                        end_date = datetime.strptime(str(self.end_date_str), fmt)
                        break
                    except ValueError:
                        continue
                
                if end_date is None:
                    print(f"Invalid end_date format: {self.end_date_str}")
                    return None, None
            except Exception as e:
                print(f"Error parsing end_date: {e}")
                return None, None

        # If either date is invalid, return None
        if start_date is None or end_date is None:
            return None, None

        india_offset_e = timedelta(hours=5, minutes=30)

        # Modify time components to set start time at 00:01 and end time at 23:59
        start_date = start_date.replace(hour=0, minute=1) - india_offset_e
        end_date = end_date.replace(hour=23, minute=59) - india_offset_e
        
        # Format the dates in the desired format with timezone
        formatted_start_date = start_date.strftime('%Y-%m-%dT%H:%M:%S%z')
        formatted_end_date = end_date.strftime('%Y-%m-%dT%H:%M:%S%z')
        
        # Ensure timezone info is included
        if not formatted_start_date.endswith('+05:30'):
            formatted_start_date = formatted_start_date.replace('+00:00', '+05:30')
        if not formatted_end_date.endswith('+05:30'):
            formatted_end_date = formatted_end_date.replace('+00:00', '+05:30')
        
        return formatted_start_date, formatted_end_date
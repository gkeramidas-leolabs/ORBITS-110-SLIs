import numpy as np
import datetime

def leap_year(year):
    """Recognizes if a year is a leap year and return boolean True if it is."""
    leap = False
    if year%4 == 0:
        if (year%100 == 0) & (year%400 == 0):
            leap = True
        elif (year%100 == 0) & (year%400 != 0):
            leap = False
        else:
            leap = True
    else:
        leap = False
        
    return leap

def next_day(year, month, day):
    """Takes one day and returns the next one."""
    leap = leap_year(year)
    day_list = [int(i) for i in np.linspace(1,31,31)]
    month_list = [int(i) for i in np.linspace(1,12,12)]
    
    if month in [1,3,5,7,8,10,12]:
        dlist = day_list
    if month == 2:
        if leap:
            dlist = day_list[0:29]
        else:
            dlist = day_list[0:28]
    if month in [4,6,9,11]:
        dlist = day_list[0:30]
        
    next_day = np.roll(dlist,-1)[day-1]
    
    if next_day == 1:
        next_month = np.roll(month_list,-1)[month-1]
    else:
        next_month = month
        
    if (next_day == 1 and next_month == 1):
        next_year = year + 1
    else:
        next_year = year
    
    return next_year,next_month, next_day


def collect_state_ids(tar_df,states_df):
    """Collects all state ids belonging to the relevant targets.
    Args: 
        tar_df: filtered targets dataframe (only relevant targets)
        states_df: states dataframe
    Returns:
        all_state_ids: List with all state ids belonging to those targets
    """
    all_state_ids = []
    for ind in tar_df.index:
        target_id = tar_df.loc[ind,'id']
        state_ids_of_target = states_df.loc[states_df['target_id']==target_id,'id']
        all_state_ids.extend(state_ids_of_target.to_list())
    return all_state_ids

def find_start_of_study(states_df):
    """Finds date of start of study, given a states dataframe. Return raw ints."""
    
    start_date = min(states_df['timestamp']).isoformat().split('T')[0]
    start_year = start_date.split('-')[0]
    start_month = start_date.split('-')[1]
    start_day = start_date.split('-')[2]
    return start_year, start_month, start_day

def find_end_of_study(states_df):
    """Finds end date of study, given a states dataframe. Returns raw ints."""
    end_date = max(states_df['timestamp']).isoformat().split('T')[0]
    end_year = end_date.split('-')[0]
    end_month = end_date.split('-')[1]
    end_day = end_date.split('-')[2]
    return end_year, end_month, end_day

class Day():
    """Class that defines a day of study.
    """
    def __init__(self,year,month,day):
        self.year = year
        self.month = month
        self.day = day
        self.states_bin = []
        self.states_bins_8hr = [[] for i in range(3)]
        self.one_day_props_1 = [[] for i in range(3)]
        self.one_day_props_2 = [[] for i in range(3)]
        self.one_day_props_3 = [[] for i in range(3)]
        self.one_day_props_rms = [[] for i in range(3)]
        self.two_day_props_1 = [[] for i in range(3)]
        self.two_day_props_2 = [[] for i in range(3)]
        self.two_day_props_3 = [[] for i in range(3)]
        self.two_day_props_rms = [[] for i in range(3)]
        self.three_day_props_1 = [[] for i in range(3)]
        self.three_day_props_2 = [[] for i in range(3)]
        self.three_day_props_3 = [[] for i in range(3)]
        self.three_day_props_rms = [[] for i in range(3)]
        self.now =[datetime.datetime(self.year,self.month,self.day,0,0,0),
                   datetime.datetime(self.year,self.month,self.day,8,0,0),
                   datetime.datetime(self.year,self.month,self.day,16,0,0)]
        
    def date_list_of_day(self):
        return [self.year,self.month,self.day]
    
    def date_string_of_day(self):
        """Method that returns the date of the day in a string."""
        if self.month < 10:
            month_str = "0" + str(self.month)
        else:
            month_str = str(self.month)
        if self.day < 10:
            day_str = "0" + str(self.day)
        else:
            day_str = str(self.day)
    
        return str(self.year) + "-" + month_str + "-" + day_str     
    
def create_day_list(states_df):
    """Function that creates a day object for each day of the study. Returns a list of days."""
    start_year,start_month,start_day = find_start_of_study(states_df)
    end_year,end_month,end_day = find_end_of_study(states_df)
    
    day_list = []
    count_of_days = 0
    year = int(start_year)
    month = int(start_month)
    day = int(start_day)
    
    while (day!=int(end_day)):
        #print(year,month,day)
        day_list.append(Day(year,month,day))
        Nyear,Nmonth,Nday = next_day(year,month,day)
        count_of_days += 1
        year = Nyear
        month = Nmonth
        day = Nday    
    return day_list

"""Functions that perform the propagation from state epoch"""

def which_state_ids_belong_to_day(state_ids,states_df,day):
    """Function that determines if a state belongs to a given day.
    Args:
        state_ids: list of all relevant state ids of the targets
        states_df: dataframe of states
        day: Object of the Day class that represents a day of the study. 
    If the state was created at that day, it's id will be added to the proper day.states_bin_8hr
    """
    
    date_string = day.date_string_of_day()
    for state_id in state_ids:
        ts_of_state = states_df.loc[(states_df['id']==state_id),'timestamp']
        hour = int((ts_of_state.iloc[0].isoformat().split('T')[1]).split(':')[0])
        if ts_of_state.iloc[0].isoformat().split('T')[0] == date_string:
            day.states_bin.append(state_id)
            if hour <=8:
                day.states_bins_8hr[0].append(state_id)
            elif (8 < hour <=16):
                day.states_bins_8hr[1].append(state_id)
            else:
                day.states_bins_8hr[2].append(state_id)
        else:          
            pass
        
def sort_states_in_days(state_ids,states_df,day_list):
    """Function that goes through all relevant state_ids and sorts them to their corresponding Day objects.
    Args:
        state_ids: list of state ids of the relevant targets
        states_df: states dataframe
        day_list: list of Day objects that represent the duration of our study
    """
    for day in day_list:
        which_state_ids_belong_to_day(state_ids,states_df,day)
        
def grab_one_day_props_for_each_day(day,props_df,states_df):
    """Function that sorts one day propagations of states to the appropriate bins. Assumes that Day objects already know which 
       state ids belong to them.
    Args:
        day: Day object
        props_df: propagations dataframe
        states_df: states dataframe
    """
    
    one_day = 24*60*60
    for bin_num in range(len(day.states_bins_8hr)):
        for state_id in day.states_bins_8hr[bin_num]:
            st_ts_series = states_df.loc[(states_df['id'] == state_id),'timestamp']
            st_ts = st_ts_series.iloc[0].timestamp()
            st_one_day_props = props_df.loc[
                    props_df['timestamp']==st_ts+1*one_day,
                    ['covariance_xx','covariance_yy','covariance_zz','Eig1','Eig2','Eig3']]
            eig_1 = st_one_day_props['Eig1'].iloc[0]
            eig_2 = st_one_day_props['Eig2'].iloc[0]
            eig_3 = st_one_day_props['Eig3'].iloc[0]
            cov_x = st_one_day_props['covariance_xx'].iloc[0]
            cov_y = st_one_day_props['covariance_yy'].iloc[0]
            cov_z = st_one_day_props['covariance_zz'].iloc[0]
            day.one_day_props_1[bin_num].append(eig_1)
            day.one_day_props_2[bin_num].append(eig_2)
            day.one_day_props_3[bin_num].append(eig_3)
            day.one_day_props_rms[bin_num].append(np.sqrt(cov_x+cov_y+cov_z))

def grab_two_day_props_for_each_day(day,props_df,states_df):
    """Function that sorts two day propagations of states to the appropriate bins. Assumes that Day objects already know which 
       state ids belong to them.
    Args:
        day: Day object
        props_df: propagations dataframe
        states_df: states dataframe
    """
    one_day = 24*60*60
    for bin_num in range(len(day.states_bins_8hr)):
        for state_id in day.states_bins_8hr[bin_num]:
            st_ts_series = states_df.loc[(states_df['id'] == state_id),'timestamp']
            st_ts = st_ts_series.iloc[0].timestamp()
            st_two_day_props = props_df.loc[
                         props_df['timestamp']==st_ts+2*one_day,
                         ['covariance_xx','covariance_yy','covariance_zz','Eig1','Eig2','Eig3']]
            eig_1 = st_two_day_props['Eig1'].iloc[0]
            eig_2 = st_two_day_props['Eig2'].iloc[0]
            eig_3 = st_two_day_props['Eig3'].iloc[0]
            cov_x = st_two_day_props['covariance_xx'].iloc[0]
            cov_y = st_two_day_props['covariance_yy'].iloc[0]
            cov_z = st_two_day_props['covariance_zz'].iloc[0]
            day.two_day_props_1[bin_num].append(eig_1)
            day.two_day_props_2[bin_num].append(eig_2)
            day.two_day_props_3[bin_num].append(eig_3)
            day.two_day_props_rms[bin_num].append(np.sqrt(cov_x+cov_y+cov_z))

def grab_three_day_props_for_each_day(day,props_df,states_df):
    """Function that sorts three day propagations of states to the appropriate bins. Assumes that Day objects already know which 
       state ids belong to them.
    Args:
        day: Day object
        props_df: propagations dataframe
        states_df: states dataframe
    """
    one_day = 24*60*60
    for bin_num in range(len(day.states_bins_8hr)):
        for state_id in day.states_bins_8hr[bin_num]:
            st_ts_series = states_df.loc[(states_df['id'] == state_id),'timestamp']
            st_ts = st_ts_series.iloc[0].timestamp()
            st_three_day_props = props_df.loc[
                         props_df['timestamp']==st_ts+3*one_day,
                         ['covariance_xx','covariance_yy','covariance_zz','Eig1','Eig2','Eig3']]
            eig_1 = st_three_day_props['Eig1'].iloc[0]
            eig_2 = st_three_day_props['Eig2'].iloc[0]
            eig_3 = st_three_day_props['Eig3'].iloc[0]
            cov_x = st_three_day_props['covariance_xx'].iloc[0]
            cov_y = st_three_day_props['covariance_yy'].iloc[0]
            cov_z = st_three_day_props['covariance_zz'].iloc[0]
            day.three_day_props_1[bin_num].append(eig_1)
            day.three_day_props_2[bin_num].append(eig_2)
            day.three_day_props_3[bin_num].append(eig_3)
            day.three_day_props_rms[bin_num].append(np.sqrt(cov_x+cov_y+cov_z))

            
def props_for_all_days(day_list,props_df,states_df):
    """Function that sorts all propagations to all days."""
    for day in day_list:
        grab_one_day_props_for_each_day(day,props_df,states_df)
        grab_two_day_props_for_each_day(day,props_df,states_df)
        grab_three_day_props_for_each_day(day,props_df,states_df)
        
"""Functions that perform the propagations from 'now'."""

def find_closest_state_of_target_to_now(target_id,states_df,now,cutoff=7):
    """Finds the closest state of a target to now.
       Args:
            target_id: id of target whose state we are looking for
            states_df: dataframe of states
            now: timestamp (in unix time) closest to which we are looking for a state
       Returns:
            closest_state_id: id of state closest to now
    """
    # All state ids of target
    state_ids_of_target = states_df.loc[states_df['target_id']==target_id,'id']
    
    closest_state_id = np.nan
    
    # timedeltas between now and state creation
    diff = []
    for state_id in state_ids_of_target:
        ts = states_df.loc[(states_df['id']==state_id),'timestamp'].iloc[0]
        if now >= ts:
            diff.append((now-ts,state_id))
    
    if diff: # Account for empty list
        # Sorted timedeltas from lowest to highest
        diffsort = sorted(diff,key=lambda x:x[0])

        # Check if closest state is within cuttof
        if diffsort[0][0]<datetime.timedelta(days=cutoff):
            closest_state_id = diffsort[0][1]
    
    return closest_state_id

def closest_states_of_targets(target_id_list,states_df,now):
    """Function that finds closest state ids of all target relative to 'now'."""
    list_of_closest_states_to_now = []
    for target_id in target_id_list:
        closest_state_id = find_closest_state_of_target_to_now(target_id,states_df,now)
        list_of_closest_states_to_now.append(closest_state_id)
    
    return list_of_closest_states_to_now

def clean_list_from_nans(A):
    """Helper function that rids a list from nans. Returns list without nans."""
    A = np.asarray(A)
    A = A[~np.isnan(A)]

    return list(A)

def sort_target_states_in_days(day_list,target_id_list,states_df):
    """Function that sorts the target states into the appropriate days 8hr bins. It does not return anything.
       For each day and each bin, it goes through the list of targets and finds exactly 1 state/target that is the closest 
       state to that bin. By the end, the 8hr bins are populated with appropriate state ids.
    """
    for day in day_list:
        for now_ind in range(3):
            now = day.now[now_ind]
            A = closest_states_of_targets(target_id_list,states_df,now)
            A = clean_list_from_nans(A)
            A = [int(x) for x in A]
            day.states_bins_8hr[now_ind].extend(A)
            
def find_prop_closest_to_x_days_from_now(state_id,states_df,props_df,now,x=1):
    """Function that finds the propagation elements of the state propagation that is closest to x days from 'now'.
       Args: 
           state_id: state for whose propagation we are going to search
           states_df: dataframe of states
           props_df: dataframe of propagations
           now: a day objects 'now' attribute
           x: number of days forward for the propagation
       Returns:
           3 eigenvalues and rms value of propagation covariance
           
    """
    one_day = 24*60*60
    
    # timestamp of the propagation we are looking for
    now_plus_1d = now.timestamp() + x*one_day
    
    # all the timestamps of propagations of the particular state
    all_props_of_state = props_df.loc[(props_df['target_state_id']==state_id),'timestamp']
    
    # timedeltas between one day from now and propagation
    diff = []
    for prop_ts in all_props_of_state:
        diff.append(((abs(now_plus_1d - prop_ts)),prop_ts))
        diffsort = sorted(diff,key=lambda x:x[0])
    # after sorting we keep the timestamp of the state whose distance from 1-day-from-now is smallest
    timestamp_of_closest_prop = diffsort[0][1]
    
    # selecting the propagation covariances of the state we specified above
    # need to bound the timestamp in order to select it
    x_day_props = props_df.loc[
                    ((props_df['target_state_id']==state_id)&
                    (props_df['timestamp']>=timestamp_of_closest_prop)&
                    (props_df['timestamp']<=(timestamp_of_closest_prop+1))),
                    ['covariance_xx','covariance_yy','covariance_zz','Eig1','Eig2','Eig3']]

    eig_1 = x_day_props['Eig1'].iloc[0]
    eig_2 = x_day_props['Eig2'].iloc[0]
    eig_3 = x_day_props['Eig3'].iloc[0]
    cov_x = x_day_props['covariance_xx'].iloc[0]
    cov_y = x_day_props['covariance_yy'].iloc[0]
    cov_z = x_day_props['covariance_zz'].iloc[0]
    
    rms = np.sqrt(cov_x+cov_y+cov_z)
    
    return eig_1, eig_2, eig_3, rms

def per_target_one_day_props_all_days(day_list, states_df, props_df):
    """Function that puts in the right bins of each day object the 1-day-from-bin-now propagation elements.
    """
    for day in day_list:
        for i in range(3):
            all_states_in_bin = day.states_bins_8hr[i]
            bin_now = day.now[i]
            for state in all_states_in_bin:
                eig_1, eig_2, eig_3, rms = find_prop_closest_to_x_days_from_now(state,states_df,props_df,bin_now,1)
                day.one_day_props_1[i].append(eig_1)
                day.one_day_props_2[i].append(eig_2)
                day.one_day_props_3[i].append(eig_3)
                day.one_day_props_rms[i].append(rms)

def per_target_three_day_props_all_days(day_list, states_df, props_df):
    """Function that puts in the right bins of each day object the 1-day-from-bin-now propagation elements.
    """
    for day in day_list:
        for i in range(3):
            all_states_in_bin = day.states_bins_8hr[i]
            bin_now = day.now[i]
            for state in all_states_in_bin:
                eig_1, eig_2, eig_3, rms = find_prop_closest_to_x_days_from_now(state,states_df,props_df,bin_now,3)
                day.three_day_props_1[i].append(eig_1)
                day.three_day_props_2[i].append(eig_2)
                day.three_day_props_3[i].append(eig_3)
                day.three_day_props_rms[i].append(rms)

"""Common Functions"""
        
def percentiles_1d_prop(day_list):
    """Function that return percentiles of one day propagation covariances from days objects. Assumes that Day objects already 
      contain their propagations.
    """
    pr110 = []
    pr125 = []
    pr150 = []
    pr175 = []
    pr195 = []
    
    pr210 = []
    pr225 = []
    pr250 = []
    pr275 = []
    pr295 = []
    
    pr310 = []
    pr325 = []
    pr350 = []
    pr375 = []
    pr395 = []
    
    prrms10 = []
    prrms25 = []
    prrms50 = []
    prrms75 = []
    prrms95 = []

    
    for day in day_list:
        for i in range(len(day.one_day_props_1)):
            if day.one_day_props_1[i]:
                pr110.append(np.percentile(day.one_day_props_1[i],10))
                pr125.append(np.percentile(day.one_day_props_1[i],25))
                pr150.append(np.percentile(day.one_day_props_1[i],50))
                pr175.append(np.percentile(day.one_day_props_1[i],75))
                pr195.append(np.percentile(day.one_day_props_1[i],95))
            else:
                pr110.append(np.nan)
                pr125.append(np.nan)
                pr150.append(np.nan)
                pr175.append(np.nan)
                pr195.append(np.nan)
            if day.one_day_props_2[i]:    
                pr210.append(np.percentile(day.one_day_props_2[i],10))
                pr225.append(np.percentile(day.one_day_props_2[i],25))
                pr250.append(np.percentile(day.one_day_props_2[i],50))
                pr275.append(np.percentile(day.one_day_props_2[i],75))
                pr295.append(np.percentile(day.one_day_props_2[i],95))
            else:
                pr210.append(np.nan)
                pr225.append(np.nan)
                pr250.append(np.nan)
                pr275.append(np.nan)
                pr295.append(np.nan)
            if day.one_day_props_3[i]:
                pr310.append(np.percentile(day.one_day_props_3[i],10))
                pr325.append(np.percentile(day.one_day_props_3[i],25))
                pr350.append(np.percentile(day.one_day_props_3[i],50))
                pr375.append(np.percentile(day.one_day_props_3[i],75))
                pr395.append(np.percentile(day.one_day_props_3[i],95))
            else:
                pr310.append(np.nan)
                pr325.append(np.nan)
                pr350.append(np.nan)
                pr375.append(np.nan)
                pr395.append(np.nan)
            if day.one_day_props_rms[i]:
                prrms10.append(np.percentile(day.one_day_props_rms[i],10))
                prrms25.append(np.percentile(day.one_day_props_rms[i],25))
                prrms50.append(np.percentile(day.one_day_props_rms[i],50))
                prrms75.append(np.percentile(day.one_day_props_rms[i],75))
                prrms95.append(np.percentile(day.one_day_props_rms[i],95))
            else:
                prrms10.append(np.nan)
                prrms25.append(np.nan)
                prrms50.append(np.nan)
                prrms75.append(np.nan)
                prrms95.append(np.nan)
            
    return pr110,pr125,pr150,pr175,pr195,\
            pr210,pr225,pr250,pr275,pr295,\
            pr310,pr325,pr350,pr375,pr395,\
            prrms10,prrms25,prrms50,prrms75,prrms95

def percentiles_2d_prop(day_list):
    """Function that return percentiles of two day propagation covariances from days objects. Assumes that Day objects already 
      contain their propagations.
    """
    pr110 = []
    pr125 = []
    pr150 = []
    pr175 = []
    pr195 = []
    
    pr210 = []
    pr225 = []
    pr250 = []
    pr275 = []
    pr295 = []
    
    pr310 = []
    pr325 = []
    pr350 = []
    pr375 = []
    pr395 = []
    
    prrms10 = []
    prrms25 = []
    prrms50 = []
    prrms75 = []
    prrms95 = []

    
    for day in day_list:
        for i in range(len(day.two_day_props_1)):
            if day.two_day_props_1[i]:
                pr110.append(np.percentile(day.two_day_props_1[i],10))
                pr125.append(np.percentile(day.two_day_props_1[i],25))
                pr150.append(np.percentile(day.two_day_props_1[i],50))
                pr175.append(np.percentile(day.two_day_props_1[i],75))
                pr195.append(np.percentile(day.two_day_props_1[i],95))
            else:
                pr110.append(np.nan)
                pr125.append(np.nan)
                pr150.append(np.nan)
                pr175.append(np.nan)
                pr195.append(np.nan)
            if day.two_day_props_2[i]:    
                pr210.append(np.percentile(day.two_day_props_2[i],10))
                pr225.append(np.percentile(day.two_day_props_2[i],25))
                pr250.append(np.percentile(day.two_day_props_2[i],50))
                pr275.append(np.percentile(day.two_day_props_2[i],75))
                pr295.append(np.percentile(day.two_day_props_2[i],95))
            else:
                pr210.append(np.nan)
                pr225.append(np.nan)
                pr250.append(np.nan)
                pr275.append(np.nan)
                pr295.append(np.nan)
            if day.two_day_props_3[i]:
                pr310.append(np.percentile(day.two_day_props_3[i],10))
                pr325.append(np.percentile(day.two_day_props_3[i],25))
                pr350.append(np.percentile(day.two_day_props_3[i],50))
                pr375.append(np.percentile(day.two_day_props_3[i],75))
                pr395.append(np.percentile(day.two_day_props_3[i],95))
            else:
                pr310.append(np.nan)
                pr325.append(np.nan)
                pr350.append(np.nan)
                pr375.append(np.nan)
                pr395.append(np.nan)
            if day.two_day_props_rms[i]:
                prrms10.append(np.percentile(day.two_day_props_rms[i],10))
                prrms25.append(np.percentile(day.two_day_props_rms[i],25))
                prrms50.append(np.percentile(day.two_day_props_rms[i],50))
                prrms75.append(np.percentile(day.two_day_props_rms[i],75))
                prrms95.append(np.percentile(day.two_day_props_rms[i],95))
            else:
                prrms10.append(np.nan)
                prrms25.append(np.nan)
                prrms50.append(np.nan)
                prrms75.append(np.nan)
                prrms95.append(np.nan)
            
    return pr110,pr125,pr150,pr175,pr195,\
            pr210,pr225,pr250,pr275,pr295,\
            pr310,pr325,pr350,pr375,pr395,\
            prrms10,prrms25,prrms50,prrms75,prrms95

def percentiles_3d_prop(day_list):
    """Function that return percentiles of two day propagation covariances from days objects. Assumes that Day objects already 
      contain their propagations.
    """
    pr110 = []
    pr125 = []
    pr150 = []
    pr175 = []
    pr195 = []
    
    pr210 = []
    pr225 = []
    pr250 = []
    pr275 = []
    pr295 = []
    
    pr310 = []
    pr325 = []
    pr350 = []
    pr375 = []
    pr395 = []
    
    prrms10 = []
    prrms25 = []
    prrms50 = []
    prrms75 = []
    prrms95 = []
    
    for day in day_list:
        for i in range(len(day.three_day_props_1)):
            if day.three_day_props_1[i]:
                pr110.append(np.percentile(day.three_day_props_1[i],10))
                pr125.append(np.percentile(day.three_day_props_1[i],25))
                pr150.append(np.percentile(day.three_day_props_1[i],50))
                pr175.append(np.percentile(day.three_day_props_1[i],75))
                pr195.append(np.percentile(day.three_day_props_1[i],95))
            else:
                pr110.append(np.nan)
                pr125.append(np.nan)
                pr150.append(np.nan)
                pr175.append(np.nan)
                pr195.append(np.nan)
            if day.three_day_props_2[i]:    
                pr210.append(np.percentile(day.three_day_props_2[i],10))
                pr225.append(np.percentile(day.three_day_props_2[i],25))
                pr250.append(np.percentile(day.three_day_props_2[i],50))
                pr275.append(np.percentile(day.three_day_props_2[i],75))
                pr295.append(np.percentile(day.three_day_props_2[i],95))
            else:
                pr210.append(np.nan)
                pr225.append(np.nan)
                pr250.append(np.nan)
                pr275.append(np.nan)
                pr295.append(np.nan)
            if day.three_day_props_3[i]:
                pr310.append(np.percentile(day.three_day_props_3[i],10))
                pr325.append(np.percentile(day.three_day_props_3[i],25))
                pr350.append(np.percentile(day.three_day_props_3[i],50))
                pr375.append(np.percentile(day.three_day_props_3[i],75))
                pr395.append(np.percentile(day.three_day_props_3[i],95))
            else:
                pr310.append(np.nan)
                pr325.append(np.nan)
                pr350.append(np.nan)
                pr375.append(np.nan)
                pr395.append(np.nan)
            if day.three_day_props_rms[i]:
                prrms10.append(np.percentile(day.three_day_props_rms[i],10))
                prrms25.append(np.percentile(day.three_day_props_rms[i],25))
                prrms50.append(np.percentile(day.three_day_props_rms[i],50))
                prrms75.append(np.percentile(day.three_day_props_rms[i],75))
                prrms95.append(np.percentile(day.three_day_props_rms[i],95))
            else:
                prrms10.append(np.nan)
                prrms25.append(np.nan)
                prrms50.append(np.nan)
                prrms75.append(np.nan)
                prrms95.append(np.nan)
            
    return pr110,pr125,pr150,pr175,pr195,\
            pr210,pr225,pr250,pr275,pr295,\
            pr310,pr325,pr350,pr375,pr395,\
            prrms10,prrms25,prrms50,prrms75,prrms95


def xtick_labels(day_list):
    """Function that return all the labels to be used for plotting for the relevant study range.
    """
    x_major_ticks_labels = []
    for day in day_list:
        x_major_ticks_labels.append(day.date_string_of_day())
    return x_major_ticks_labels

def x_plottings(percentile_list):
    """Function that returns number of bins to be plotted against and tick locations to be used.
    Args:
        percentile_list: list of percentiles to be plotted
    Returns: 
        xs: bins that percentiles are to be plotted (x-axis)
        x_t: location of ticks of the x-axis
    """
    xs = [i for i in range(len(percentile_list))]
    x_t = [i for i in range(len(percentile_list)+1)]
    return xs, x_t

def add_eig_columns_to_props(props_df):
    """Function that adds 3 principal eigenvectors of the covariance matrix to the propagations dataframe"""
    xx = props_df["covariance_xx"].values
    xy = props_df["covariance_xy"].values
    xz = props_df["covariance_xz"].values
    yy = props_df["covariance_yy"].values
    yz = props_df["covariance_yz"].values
    zz = props_df["covariance_zz"].values
    
    A = np.stack((xx,xy,xz,xy,yy,yz,xz,yz,zz),axis=1)
    
    eig1 = []
    eig2 = []
    eig3 = []
    for i in range(len(props_df)):
        B = np.reshape(A[i,:],(3,3))
        eigs_B = np.linalg.eigvals(B)
        eigs_B = sorted(eigs_B,reverse=True)
        eig1.append(eigs_B[0])
        eig2.append(eigs_B[1])
        eig3.append(eigs_B[2])
    
    props_df["Eig1"] = eig1
    props_df["Eig2"] = eig2
    props_df["Eig3"] = eig3
    
    return props_df
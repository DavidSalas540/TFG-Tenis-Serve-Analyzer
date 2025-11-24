import pandas as pd


def ankle_variation(df_csv):
    
    max_frame = max_knee(df_csv)
    
    
    for i in max_frame:
        difference_x = df_csv['LEFT_ANKLE_x'] - df_csv['RIGHT_ANKLE_x']   
    
    
    
    pass


def max_knee(df_csv):
    pass



def metrics_pipeline(df_csv):
    pass
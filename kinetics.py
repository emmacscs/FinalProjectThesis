import pandas as pd

def run(df_har):
    # Create a copy of df_har for the kinetics DataFrame
    df_kinetics = df_har.copy()

    # Constants for the Kinetics
    ka1 = 0.0164  # Absorption rate constant for nonmonomeric insulin (min^-1)
    ka2 = 0.0182  # Absorption rate constant for monomeric insulin (min^-1)
    kd = 0.0076   # Dissociation rate constant (min^-1)

    df_kinetics['Insulin absorption'] = pd.Series(dtype='float')
    # Add the column for carbohydrate absorption
    df_kinetics['Carbs absorption'] = pd.Series(dtype='float')


    # Reset index, and set the start of the index to 1 instead of 0
    df_kinetics.reset_index(drop=True, inplace=True)
    df_kinetics.index += 1  # Add 1 to the index to start from 1

        # Loop to iterate through df_kinetics and calculate insulin absorption and carbohydrate absorption
    for i in range(1, len(df_kinetics)):
        # Initialize insulin concentrations for this interval
        I_scl1 = 0.25  # Initial nonmonomeric insulin concentration (subcutaneous space)
        I_scl2 = 0.25  # Initial monomeric insulin concentration (subcutaneous space)
        I_scs = 0.25   # Initial insulin concentration in the bloodstream
        
        # Initialize carbohydrate concentrations for this interval
        C_scl1 = 0.25  # Initial nonmonomeric carbohydrate concentration (subcutaneous space)
        C_scl2 = 0.25  # Initial monomeric carbohydrate concentration (subcutaneous space)
        C_scs = 0.25   # Initial carbohydrate concentration in the bloodstream

        # For rapid insulin injection
        if df_kinetics.at[i, 'Rapid Insulin'] > 0:
            u = df_kinetics.at[i, 'Rapid Insulin']  # Total infusion rate for rapid insulin

            # Loop through the current and following intervals (30 or 50 intervals)
            for j in range(i, min(i + 50, len(df_kinetics))):
                # Calculate the time difference in minutes as an integer
                t = (df_kinetics.iloc[j]['Time'] - df_kinetics.iloc[i]['Time']).total_seconds() // 60  # Convert to minutes
                
                # Apply the compartment model for rapid insulin
                I_scl1 = I_scl1 + (- (ka1 + ka1) * I_scl1) + u * 15  # Time step = 15 minutes
                I_scl2 = I_scl2 + (ka1 * I_scl1 - ka2 * I_scl2) * 15
                I_scs = I_scs + (ka2 * I_scl2 - kd * I_scs) * 15

                # Compute the insulin absorption (Ri) for this period
                insulin_absorbed = ka1 * I_scl1 - ka2 * I_scl2

                # Store the absorption value for this time step
                df_kinetics.at[j, 'Insulin absorption'] = insulin_absorbed

                # If absorption becomes negligible, break the loop
                if I_scs < 0.1:  # Set threshold for negligible absorption
                    break

        # For long insulin injection
        if df_kinetics.at[i, 'Long Insulin'] > 0:
            u = df_kinetics.at[i, 'Long Insulin']  # Total infusion rate for long insulin

            # Loop through the current and following intervals (30 or 50 intervals)
            for j in range(i, min(i + 50, len(df_kinetics))):
                # Calculate the time difference in minutes as an integer
                t = (df_kinetics.iloc[j]['Time'] - df_kinetics.iloc[i]['Time']).total_seconds() // 60  # Convert to minutes
                
                # Apply the compartment model for long insulin
                I_scl1 = I_scl1 + (- (ka1 + ka1) * I_scl1) + u   # Time step = 15 minutes
                I_scl2 = I_scl2 + (ka1 * I_scl1 - ka2 * I_scl2) 
                I_scs = I_scs + (ka2 * I_scl2 - kd * I_scs) 

                # Compute the insulin absorption (Ri) for this period
                insulin_absorbed = ka1 * I_scl1 - ka2 * I_scl2

                # Store the absorption value for this time step
                df_kinetics.at[j, 'Insulin absorption'] = insulin_absorbed

                # If absorption becomes negligible, break the loop
                if I_scs < 0.1:  # Set threshold for negligible absorption
                    break

        # For carbohydrate absorption (similar to insulin)
        if df_kinetics.at[i, 'Carbohydrates'] > 0:
            u_carbs = df_kinetics.at[i, 'Carbohydrates']  # Total carbohydrate intake for this time step

            # Loop through the current and following intervals for carbohydrates (30 or 50 intervals)
            for j in range(i, min(i + 50, len(df_kinetics))):
                # Calculate the time difference in minutes as an integer
                t = (df_kinetics.iloc[j]['Time'] - df_kinetics.iloc[i]['Time']).total_seconds() // 60  # Convert to minutes
                
                # Apply the compartment model for carbohydrates (similar to insulin model)
                C_scl1 = C_scl1 + (- (ka1 + ka1) * C_scl1) + u * 15  # Time step = 15 minutes
                C_scl2 = C_scl2 + (ka1 * C_scl1 - ka2 * C_scl2) * 15
                C_scs = C_scs + (ka2 * C_scl2 - kd * C_scs) * 15

                # Compute the carbohydrate absorption (Ri) for this period
                carbs_absorbed = ka1 * C_scl1 - ka2 * C_scl2

                # Store the carbohydrate absorption value for this time step
                df_kinetics.at[j, 'Carbs absorption'] = carbs_absorbed

                # If absorption becomes negligible, break the loop
                if C_scs < 0.1:  # Set threshold for negligible absorption
                    break

    return df_kinetics


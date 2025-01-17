import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import numpy as np
import sys, os
import sqlite3
import plotly.figure_factory as ff
import plotly.express as px







def format_column_name(column_name):
    """
    This function takes a column name as input, replaces underscores with spaces,
    and capitalizes the first letter of each word.

    Parameters:
    - column_name (str): The input string that needs to be formatted.

    Returns:
    str: The formatted string with spaces instead of underscores and capitalized words.
    """
    # Replacing underscores with spaces
    name_with_spaces = column_name.replace('_', ' ')
    
    # Capitalizing the first letter of each word
    user_friendly_name = name_with_spaces.title()
    
    return user_friendly_name





def get_simulation_data(db, dataset_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db)
    # Read the data from the SQLite table into a DataFrame
    df = pd.read_sql(f'SELECT * FROM {dataset_name}', conn)

    # Close the connection
    conn.close()
    return df

def plot_results_plotly(x, y_columns, run, param_id):

    df = get_simulation_data('simulationData.db', 'simulation_data_'+param_id)

    # example for Monte Carlo plots
    #monte_carlo_plot_st(df,'timestep','timestep','seed_a_tokens_vested_cum',3)

    # example for line plots of different outputs in one figure
    line_plot_plotly(df,x, y_columns, run)



def aggregate_runs(df,aggregate_dimension,x,y):
    '''
    Function to aggregate the monte carlo runs along a single dimension.

    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.

    Example run:
    mean_df,median_df,std_df,min_df = aggregate_runs(df,'timestep')
    '''
    df = df[[x,y]].copy()
    mean_df = df.astype(float).groupby(aggregate_dimension).mean().reset_index()
    median_df = df.astype(float).groupby(aggregate_dimension).median().reset_index()
    std_df = df.astype(float).groupby(aggregate_dimension).std().reset_index()
    min_df = df.astype(float).groupby(aggregate_dimension).min().reset_index()

    return mean_df,median_df,std_df,min_df

# 
def monte_carlo_plot(df,aggregate_dimension,x,y,runs):
    '''
    A function that generates timeseries plot of Monte Carlo runs.

    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.
    x = x axis variable for plotting
    y = y axis variable for plotting
    run_count = the number of monte carlo simulations

    Example run:
    monte_carlo_plot(df,'timestep','timestep','revenue',run_count=100)
    '''
    mean_df,median_df,std_df,min_df = aggregate_runs(df,aggregate_dimension,x,y)

    plt.figure(figsize=(10,6))
    for r in range(1,runs+1):
        legend_name = 'Run ' + str(r)
        plt.plot(df[df.run==r].timestep, df[df.run==r][y], label = legend_name )
    
    plt.plot(mean_df[x], mean_df[y], label = 'Mean', color = 'black')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.xlabel(x)
    plt.ylabel(y)
    title_text = 'Performance of ' + y + ' over ' + str(runs) + ' Monte Carlo Runs'
    plt.title(title_text)

def monte_carlo_plot_st(df,aggregate_dimension,x,y,runs):
    '''
    A function that generates timeseries plot of Monte Carlo runs.

    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.
    x = x axis variable for plotting
    y = y axis variable for plotting
    run_count = the number of monte carlo simulations

    Example run:
    monte_carlo_plot(df,'timestep','timestep','revenue',run_count=100)
    '''
    fig = plt.figure(figsize=(10,6))
    if runs > 1:
        for r in range(1,runs+1):
            legend_name = 'Run ' + str(r)
            plt.plot(np.asarray(df[df['run'].astype(int)==r].timestep, float), np.asarray(df[df['run'].astype(int)==r][y], float), label = legend_name )
        mean_df,median_df,std_df,min_df = aggregate_runs(df,aggregate_dimension,x,y)
        plt.plot(np.asarray(mean_df[x], float), np.asarray(mean_df[y], float), label = 'Mean', color = 'black')
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    
    else:
        plt.plot(np.asarray(df[df['run'].astype(int)==1].timestep, float), np.asarray(df[df['run'].astype(int)==1][y], float))
    plt.xlabel(x)
    plt.ylabel(y)
    title_text = 'Performance of ' + y + ' over ' + str(runs) + ' Monte Carlo Runs'
    plt.title(title_text)

    st.pyplot(fig)


def line_plot_plotly(df,x,y_series,run):
    '''
    A function that generates a line plot from a series of data series in a frame in streamlit
    '''
    
    chart_data = pd.DataFrame(np.asarray(df[df['run'].astype(int)==run][[x]+y_series], float), columns=[x]+y_series)


    #fig = px.line(chart_data, x=x, y=y_series)


    # Format the column names
    formatted_columns = [format_column_name(col) for col in [x] + y_series]
    chart_data.columns = formatted_columns
    
    fig = px.line(chart_data, x=formatted_columns[0], y=formatted_columns[1:])


    st.plotly_chart(fig, use_container_width=True)

def bar_plot_plotly(values_list, param_id):
    # Check if the values in values_list exist in the DataFrame
    
    sys_param_df = get_simulation_data('simulationData.db', 'sys_param')
    sys_param = sys_param_df[sys_param_df['id'] == param_id]

    df = sys_param[values_list].sum().to_frame(name='Value').reset_index().rename(columns={'index':'Parameter'})
    
    # Format the 'Parameter' column
    df['Parameter'] = df['Parameter'].apply(format_column_name)

    fig = px.bar(df, x='Parameter', y='Value')

    st.plotly_chart(fig, use_container_width=True)





def pie_plot_plotly(values_list, param_id):
    # Check if the values in values_list exist in the DataFrame
    
    sys_param_df = get_simulation_data('simulationData.db', 'sys_param')
    sys_param = sys_param_df[sys_param_df['id'] == param_id]

    df = sys_param[values_list].sum().to_frame(name='Value').reset_index().rename(columns={'index':'Parameter'})

    # Format the 'Parameter' column
    df['Parameter'] = df['Parameter'].apply(format_column_name)

    # drop zero parameters
    df = df[df['Value'] != 0]
    fig = px.pie(df, values='Value', names='Parameter')

    st.plotly_chart(fig, use_container_width=True)







def plot_all_plotly(param_id):    
    ##FUNDRAISING TAB
    plot_results_plotly('timestep', ['seed_a_tokens_vested_cum','angle_a_tokens_vested_cum',
            'team_a_tokens_vested_cum','reserve_a_tokens_vested_cum','presale_1_a_tokens_vested_cum'], 1, param_id)
        ##NEED EFFECTIVE TOKEN PRICE
    bar_plot_plotly([
        'angle_token_effective',
        'seed_token_effective',
        'presale_1_token_effective',
        'presale_2_token_effective',
        'public_token_effective'
    ], param_id)
        ##NEED PIE CHART OF INITIAL ALLOCATION
    pie_plot_plotly([
        'angle_token_allocation',
        'seed_token_allocation',
        'presale_1_token_allocation',
        'presale_2_token_allocation',
        'public_sale_token_allocation',
        'team_token_allocation',
        'ov_token_allocation',
        'advisor_token_allocation',
        'strategic_partners_token_allocation',
        'reserve_token_allocation',
        'community_token_allocation',
        'foundation_token_allocation',
        'incentivisation_token_allocation',
        'staking_vesting_token_allocation',
        'airdrop_token_allocation',
        'market_token_allocation',
        'airdrop_receivers_token_allocation',
        'incentivisation_receivers_token_allocation'
    ], param_id)

    ##INPUTS TAB
    plot_results_plotly('timestep', ['ua_product_users','ua_token_holders'], 1, param_id)
    plot_results_plotly('timestep', ['ua_product_revenue'], 1, param_id)
    plot_results_plotly('timestep', ['ua_token_buys'], 1, param_id)
    plot_results_plotly('timestep', ['ba_cash_balance'], 1, param_id)

    ##UTILITIES TAB
    pie_plot_plotly(['lock_share','lock_vesting_share','liquidity_mining_share','burning_share',
                     'holding_share','transfer_share','lock_buyback_distribute_share'], param_id)

    ##ANALYSIS TAB
    plot_results_plotly('timestep', ['reserve_a_tokens','community_a_tokens','foundation_a_tokens','incentivisation_a_tokens','staking_vesting_a_tokens','lp_tokens','te_holding_supply','te_unvested_supply','te_circulating_supply'], 1, param_id)
    plot_results_plotly('timestep', ['lp_token_price','lp_volatility'], 1, param_id)
    plot_results_plotly('timestep', ['lp_token_price','te_MC','te_FDV_MC'], 1, param_id)
    plot_results_plotly('timestep', ['u_staking_base_apr_allocation_cum','u_staking_revenue_share_allocation_cum','u_staking_vesting_allocation_cum','u_liquidity_mining_allocation_cum','u_burning_allocation_cum','u_transfer_allocation_cum','te_incentivised_tokens_cum','te_airdrop_tokens_cum','te_holding_allocation_cum'], 1, param_id)
    plot_results_plotly('timestep', ['u_staking_base_apr_allocation','u_staking_revenue_share_allocation','u_staking_vesting_allocation','u_liquidity_mining_allocation','u_burning_allocation','u_transfer_allocation','te_incentivised_tokens','te_airdrop_tokens','te_holding_allocation'], 1, param_id)

def plot_fundraising(param_id):    
    ##FUNDRAISING TAB
    plot_results_plotly('timestep', ['seed_a_tokens_vested_cum','angle_a_tokens_vested_cum','team_a_tokens_vested_cum',
                                     'reserve_a_tokens_vested_cum','presale_1_a_tokens_vested_cum'], 1, param_id)
        ##NEED EFFECTIVE TOKEN PRICE
    bar_plot_plotly([
        'angle_token_effective',
        'seed_token_effective',
        'presale_1_token_effective',
        'presale_2_token_effective',
        'public_token_effective'
    ], param_id)
        ##NEED PIE CHART OF INITIAL ALLOCATION
    pie_plot_plotly([
        'angle_token_allocation',
        'seed_token_allocation',
        'presale_1_token_allocation',
        'presale_2_token_allocation',
        'public_sale_token_allocation',
        'team_token_allocation',
        'ov_token_allocation',
        'advisor_token_allocation',
        'strategic_partners_token_allocation',
        'reserve_token_allocation',
        'community_token_allocation',
        'foundation_token_allocation',
        'incentivisation_token_allocation',
        'staking_vesting_token_allocation',
        'airdrop_token_allocation',
        'market_token_allocation',
        'airdrop_receivers_token_allocation',
        'incentivisation_receivers_token_allocation'
    ], param_id)

def plot_business(param_id):    
    ##INPUTS TAB
    plot_results_plotly('timestep', ['ua_product_users','ua_token_holders'], 1, param_id)
    plot_results_plotly('timestep', ['ua_product_revenue'], 1, param_id)
    plot_results_plotly('timestep', ['ua_token_buys'], 1, param_id)
    plot_results_plotly('timestep', ['ba_cash_balance'], 1, param_id)

def plot_token_economy(param_id):
    ##UTILITIES TAB
    pie_plot_plotly(['lock_share','lock_vesting_share','liquidity_mining_share','burning_share',
                     'holding_share','transfer_share','lock_buyback_distribute_share'], param_id)

    ##ANALYSIS TAB
    plot_results_plotly('timestep', ['reserve_a_tokens','community_a_tokens','foundation_a_tokens','incentivisation_a_tokens','staking_vesting_a_tokens','lp_tokens','te_holding_supply','te_unvested_supply','te_circulating_supply'], 1, param_id)
    plot_results_plotly('timestep', ['lp_token_price','lp_volatility'], 1, param_id)
    plot_results_plotly('timestep', ['lp_token_price','te_MC','te_FDV_MC'], 1, param_id)
    plot_results_plotly('timestep', ['u_staking_base_apr_allocation_cum','u_staking_revenue_share_allocation_cum','u_staking_vesting_allocation_cum','u_liquidity_mining_allocation_cum','u_burning_allocation_cum','u_transfer_allocation_cum','te_incentivised_tokens_cum','te_airdrop_tokens_cum','te_holding_allocation_cum'], 1, param_id)
    plot_results_plotly('timestep', ['u_staking_base_apr_allocation','u_staking_revenue_share_allocation','u_staking_vesting_allocation','u_liquidity_mining_allocation','u_burning_allocation','u_transfer_allocation','te_incentivised_tokens','te_airdrop_tokens','te_holding_allocation'], 1, param_id)




from flask import Flask, request, jsonify

import pandas as pd

import numpy as np

from datetime import datetime

import os

app = Flask(__name__)

 

@app.route('/simulate', methods=['POST'])

def simulate():

    # Get parameters from request

    data = request.get_json()

    user_id = data.get('userId')

    random_seed = int(data.get('randomSeed', 123))

    number_of_rows = int(data.get('numberOfRows', 10000))

 

    # Set random seed

    np.random.seed(random_seed)

 

    # Generate observedTemperature (uniform between 20 and 90 Fahrenheit)

    observed_temp = np.random.uniform(20, 90, number_of_rows)

 

    # Convert observedTemperature to Celsius

    observed_temp_c = (observed_temp - 32) * 5.0 / 9.0

 
# ---- Add right-tail variance to predicted temperature ----
    # Instead of symmetric normal noise, use a right-skewed (lognormal) noise
    # This will produce higher variability on the positive side (right tail)
    base_noise = np.random.normal(0, 1, number_of_rows)
    right_tail_noise = np.random.lognormal(mean=0, sigma=0.3, size=number_of_rows) - np.exp(0.3**2 / 2)
    
    # Combine symmetric and right-skewed components
    skewed_noise = 0.7 * base_noise + 0.3 * right_tail_noise
    
    # Apply the noise to observed temperature
    predicted_temp_c = observed_temp_c + skewed_noise

    # Disturb predictedTemperature by adding normal noise
    right_tail_noise = np.random.lognormal(mean=0.3, sigma=0.6, size=number_of_rows)
    right_tail_noise = right_tail_noise - np.mean(right_tail_noise) * 0.4
    bias_factor = (observed_temp_c - observed_temp_c.min()) / (observed_temp_c.max() - observed_temp_c.min())
    predicted_temp_c = observed_temp_c + 0.3 * right_tail_noise + 2 * bias_factor

    # Create DataFrame

    df = pd.DataFrame({

        'rowId': np.arange(1, number_of_rows + 1),

        'predictedTemperature_Celsius': predicted_temp_c,

        'observedTemperature_Fahrenheit': observed_temp

    })

 

      # This dictionary describes the task for the candidate.

    task_description = {

        "objective": "Creating a Q-Q plot based on data extracted.",

        "More": [

            "Congrats! You successfully accessed API!",

            "Please create the 20-quantile Q-Q plot from the simulated data, making sure the plot is interpretable."

              ]

    }

 

    # Prepare response

    response = {

        'userId': user_id,

        'randomSeed': random_seed,

        'dateTimeStamp': datetime.utcnow().isoformat(),

        'taskDescription': task_description, # Added the new component here

        'simulatedData': df.to_dict(orient='records')

    }

 

    return jsonify(response)

 

#if __name__ == '__main__':

#    app.run(debug=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render provides PORT automatically
    app.run(host='0.0.0.0', port=port, debug=True)




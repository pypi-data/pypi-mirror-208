import requests

class Arc:
    def __init__(self, props):
        self.key = props['key']
        self.uid = props['uid']
        self.name = props['name']

    def chat(self, user_input):
        # Define the API endpoint URL
        url = 'https://api.arcangelai.com/arc/v2'

        # Set the API key in the header
        headers = {'X-API-KEY': self.key}

        # Set the message in the body as a JSON object
        data = {
            'message': user_input,
            'uid': self.uid,
            'name': self.name
        }

        # Make the API post request
        response = requests.post(url, headers=headers, json=data)

       # Check if the API call was successful
        if response.status_code == 200:
            # Get the JSON response
            json_response = response.json()
            return json_response
        elif response.status_code == 429:
            return {"code": str(response.status_code), "message": str(response.text)}
        else:
            return {"code": str(response.status_code), "message": str(response.text)}



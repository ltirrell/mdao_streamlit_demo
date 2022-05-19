# MetricsDAO Streamlit Demo
This is a basic overview of using [Streamlit](https://streamlit.io/) to create interactive dashboards using [Altair](https://altair-viz.github.io/) visualizations.

## Setup
To get started, clone this repo, cd into it and run:
```
pip install -r requirements.txt
```

Alternatively, to just setup your Python environment to include packages needed for this demo, run:
```
pip install streamlit altair vega_datasets
```

### Optional: Streamlit Cloud
One advantage of Streamlit is being able to create a sharable web page directly from a GitHub repo.
Sign up for [Streamlit Cloud](https://streamlit.io/cloud) and connect your GitHub account, then your dashboard can be shared with the world!

Without signing up for a cloud account, you can still run examples locally on your computer, or self host your dashboard (out of scope for this demo).


## Streamlit basics
- Check out the [Gallery](https://streamlit.io/gallery) for some great examples!
- The [docs](https://docs.streamlit.io/) are great, with getting started guide and links to more help (such as a community forum).
- The [API reference](https://docs.streamlit.io/library/api-reference) is a great way to figure out what you can do with streamlit!

## Run a Streamlit app
Use `streamlit run my_app.py` to run your app.
You can then open it locally from your web browser with the URL printed to your terminal (such as http://localhost:8501).

To run the basic app (taken from the [Getting Started](https://docs.streamlit.io/library/get-started/create-an-app) page), run:
```
streamlit run basic_app.py 
```

For our more complex example, run:
```
streamlit run solana_swaps.py
```

## Deploy your app!
If you signed up for Streamlit Cloud, you can now deploy your app!
Just push your code to a GitHub repo, and follow instructions [here](https://docs.streamlit.io/streamlit-cloud/get-started).
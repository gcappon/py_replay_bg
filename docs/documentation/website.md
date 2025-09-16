# ReplayBG DEMO website

The demo website showcases the main features of ReplayBG, allowing users to explore its capabilities in a user-friendly
environment.

## Point system

The website is based on a point system to manage the computational resources effectively.

Each registered user receives **200 points** upon registration. Points are used as follows:
- **3 points** per digital twin creation
- **1 point** per replay simulation

If your point balance is depleted, request additional points by contacting the developers at [replaybg.dei@gmail.com](mailto:replaybg.dei@gmail.com).


## Creation of digital twins

The website allows registered users to create digital twins by uploading their own data or using sample datasets
provided on the platform.
Users can then download the generated digital twins for further analysis.

### Upload of past digital twins

Users can upload previously created digital twins in `.pkl` format to the platform for further simulations and analyses.

## Simulation of alternative therapies

Users can simulate various alternative therapies using the digital twins created on the platform.
The website provides an intuitive interface to select and customize different therapy options, enabling users to assess
their potential impact on glucose management.
The simulation results can be downloaded for further analysis.

### Create, edit or remove events

The platform allows users to create, edit, or remove events such as meals, insulin doses, and basal insulin with an
easy-to-use interface, which makes the user directly interact with the data plotted on the graphs.

### Scale input data

With the provided sliders in the top right panel, it is easy to scale input data (e.g., carbohydrate intake, insulin
doses) to simulate different scenarios and evaluate
their effects.

### Custom algorithms and advanced handlers

The website supports the integration of custom algorithms and advanced handlers, allowing users to tailor the simulation
to their specific needs and research objectives.
It is possible to enable the default handlers provided by the tool or create new ones as `.py` files by following the
instructions in
the [documentation](./replaying.md#event-handlers).
It is also possible to upload a `.txt` file containing the parameters for the handlers.

## Visualization and statistics

The website includes interactive visualization tools of the data and shows basic statistics to help users interpret the
simulation results.
A comprehensive report of differences between original data and custom simulations is also possible to be downloaded.

## Error Handling and Support

For troubleshooting and support, contact the development team at [replaybg.dei@gmail.com](mailto:replaybg.dei@gmail.com).

## Data Privacy and Security

Uploaded data is handled securely and used solely for simulation purposes. Authentication is required for all core features.
All data is deleted after 7 days from the upload.

## Try it out!

You can try out the demo at [https://replaybg.duckdns.org](https://replaybg.duckdns.org).
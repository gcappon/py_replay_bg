import numpy as np

from py_replay_bg.sensors.CGM import CGM


class DexcomG6(CGM):
    """
    A class that represents a DexcomG6 CGM sensor.

    Attributes
    ----------
    ts: int
        The sample time of the cgm sensor (min).
    t_offset: float
        The time offset of the cgm sensor (when new this is 0). This is used if a cgm sensor is shared between more
        replay runs.
    cgm_error_parameters: np.ndarray
        An array containing the parameters of the CGM.
    output_noise_sd: float
        The output standard deviation of the CGM error model.
    ekm1: float
        Memory term for the CGM noise: e(k-1).
   ekm2: float
        Memory term for the CGM noise: e(k-2).
    max_lifetime: float
        The maximum lifetime of the CGM sensor (in minutes).
    connected_at: int
        The time at which the CGM sensor is connected (utility variable to manage sensor lifetime through multiple
        ReplayBG calls).

    Methods
    -------
    connect_new_cgm(connected_at):
        Connects a new CGM sensor by sampling new error parameters.
    measure(ig, t):
        Function that provides a CGM measure using the model of Vettoretti et al., Sensors, 2019.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the CGM object.

        Parameters
        ----------
        ts: int, optional, default = 5
            The sample time of the cgm sensor (min).
        """
        super().__init__()

        # Set the parameters of the CGM
        self.cgm_error_parameters = []
        self.output_noise_sd = []

        # Set memory terms
        self.ekm1 = None
        self.ekm2 = None

    def connect_new_cgm(self, connected_at=0):
        """
        Connects a new CGM sensor by sampling new error parameters.

        Parameters
        ----------
        connected_at: int, optional, default = 0
            The time at which the CGM sensor is connected (utility variable to manage sensor lifetime through multiple
            ReplayBG calls).

        Returns
        -------
        None

        Raises
        ------
        None

        See Also
        --------
        None

        Examples
        --------
        None
        """

        super().connect_new_cgm(connected_at)

        # Load  Mean vector and covariance matrix of the parameter vector as
        # defined in Vettoretti et al., Sensors, 2019
        mu = np.array([0.94228767821000314341972625697963, 0.0049398821141803427384187052950892,
                       -0.0005848748565491275084801681138913, 6.382602204050874306062723917421,
                       1.2604070417357611244568715846981, -0.4022228938823663169088717950217,
                       3.2516360856114072674927228945307])
        sigma = np.array([[0.013245827952891258902368143424155, -0.0039513025350735725416129184850433,
                           0.00031276743283791636970891936186945, 0.15717912467153988265167186000326,
                           0.0026876560011614997885986966252858, -0.0028904633825263671524641306831427,
                           -0.0031801707001874032418320403792222],
                          [-0.0039513025350735725416129184850433, 0.0018527975980744701509778105119608,
                           -0.00015580332205794781403294935184789, -0.10288007693621757654423021222101,
                           -0.0013902327543057948350258001823931, 0.0011591852212130876378232136048041,
                           -0.0027284927011686846420879248853453],
                          [0.00031276743283791636970891936186945, -0.00015580332205794781403294935184789,
                           0.000013745962164724157000697882247131, 0.0080685863688738888865881193623864,
                           0.00012074974710011031125631020266553, -0.00010042135441622312822841645019167,
                           0.00011130290033867137325027107941366],
                          [0.15717912467153988265167186000326, -0.10288007693621757654423021222101,
                           0.0080685863688738888865881193623864, 29.005838188852990811028575990349,
                           0.12408344051778112671069465022811, -0.10193644943826736526393261783596,
                           0.60075381294204155402383094042307],
                          [0.0026876560011614997885986966252858, -0.0013902327543057948350258001823931,
                           0.00012074974710011031125631020266553, 0.12408344051778112671069465022811,
                           0.02079352674233487727195601735275, -0.018431109170459980539646949182497,
                           -0.015721846813032722134373386779771],
                          [-0.0028904633825263671524641306831427, 0.0011591852212130876378232136048041,
                           -0.00010042135441622312822841645019167, -0.10193644943826736526393261783596,
                           -0.018431109170459980539646949182497, 0.018700867933453400870913441167431,
                           0.01552333576829629385729347745837],
                          [-0.0031801707001874032418320403792222, -0.0027284927011686846420879248853453,
                           0.00011130290033867137325027107941366, 0.60075381294204155402383094042307,
                           -0.015721846813032722134373386779771, 0.01552333576829629385729347745837,
                           0.72356838038463477946748980684788]])

        # Modulation factor of the covariance of the parameter vector not to generate too extreme realizations of
        # parameter vector
        f = 0.90
        # Modulate the covariance matrix
        sigma = sigma * f
        # Maximum allowed output noise SD (mg/dl)
        max_output_noise_sd = 10
        # Tolerance for model stability check
        toll = 0.02

        # Flag for stability of the AR(2) model
        stable = 0
        output_noise_sd = np.inf
        cgm_error_parameters = []
        while (~ stable) or (output_noise_sd > max_output_noise_sd):
            # Sample CGM error parameters
            cgm_error_parameters = np.random.multivariate_normal(mu, sigma)

            # Check the stability of the resulting AR(2) model
            stable = (cgm_error_parameters[5] >= -1) and (
                    cgm_error_parameters[5] <= (1 - np.abs(cgm_error_parameters[4]) - toll))

            output_noise_var = cgm_error_parameters[6] ** 2 / (
                    1 - (cgm_error_parameters[4] ** 2) / (1 - cgm_error_parameters[5]) - cgm_error_parameters[5] * (
                    (cgm_error_parameters[4] ** 2) / (1 - cgm_error_parameters[5]) + cgm_error_parameters[5]))

            if output_noise_var < 0:
                continue

            # Compute the output noise standard deviation
            output_noise_sd = np.sqrt(output_noise_var)

        # Set the parameters of the CGM
        self.cgm_error_parameters = cgm_error_parameters
        self.output_noise_sd = output_noise_sd

        # Set memory terms
        self.ekm1 = 0
        self.ekm2 = 0


    def measure(self, ig, past_ig, t):
        """
        Function that provides a CGM measure using the model of Vettoretti et al., Sensors, 2019.

        Parameters
        ----------
        ig: float
            The current interstitial glucose concentration (mg/dl).
        past_ig: list[float]
            The series of past interstitial glucose concentrations (mg/dl). The value of ig[-1] is the current interstitial glucose.
        t: float
            Current time in days from the start of CGM sensor.

        Returns
        -------
        cgm: float
            The CGM measurement at current time (mg/dl).

        Raises
        ------
        None

        See Also
        --------
        None

        Examples
        --------
        None
        """

        # Apply calibration error
        ig_s = (self.cgm_error_parameters[0] + self.cgm_error_parameters[1] * (t + self.t_offset) +
                self.cgm_error_parameters[2] * ((t + self.t_offset) ** 2)) * ig + self.cgm_error_parameters[3]

        # Generate noise
        z = np.random.normal(0, 1)
        u = self.cgm_error_parameters[6] * z
        e = u + self.cgm_error_parameters[4] * self.ekm1 + self.cgm_error_parameters[5] * self.ekm2

        # Update memory terms
        self.ekm2 = self.ekm1
        self.ekm1 = e

        # Get final CGM
        return ig_s + e

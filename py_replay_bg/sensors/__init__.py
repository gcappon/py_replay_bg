import numpy as np


class Sensors:
    """
    A class that represents the sensors to be used by ReplayBG.

    ...
    Attributes
    ----------
    cgm: CGM
        The CGM sensor used to measure the interstitial glucose during simulations.

    Methods
    -------
    None
    """

    def __init__(self, cgm):
        """
        Constructs all the necessary attributes for the Sensors object.

        Parameters
        ----------
        cgm: CGM
            The CGM sensor used to measure the interstitial glucose during simulations.
        """
        self.cgm = cgm


class CGM:
    """
    A class that represents a CGM sensor.

    ...
    Attributes
    ----------
    ts: int
        The sample time of the cgm sensor (min).
    model: string, {'CGM','IG'}
        A string that specifies the cgm model selection.
        If IG is selected, CGM measure will be the noise-free IG state at the current time.
    cgm_error_parameters: array
        An array containing the parameters of the CGM.
    output_noise_SD: float
        The output standard deviation of the CGM error model.

    Methods
    -------
    connect_new_cgm():
        Connects a new CGM sensor by sampling new error parameters.
    measure(IG, t):
        Function that provides a CGM measure using the model of Vettoretti et al., Sensors, 2019.
    """

    def __init__(self, ts=5, model='CGM'):
        """
        Constructs all the necessary attributes for the CGM object.

        Parameters
        ----------
        ts: int, optional, default = 5
            The sample time of the cgm sensor (min).
        model: string, {'CGM','IG'}, optional, default : 'CGM'
            A string that specify the cgm model selection.
            If IG is selected, CGM measure will be the noise-free IG state at the current time.
        """
        self.ts = ts
        self.model = model

        if self.model == 'CGM':
            self.connect_new_cgm()
        else:
            self.cgm_error_parameters, self.output_noise_SD = [], []

    def connect_new_cgm(self):
        """
        Connects a new CGM sensor by sampling new error parameters.

        Parameters
        ----------
        None

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
        max_output_noise_SD = 10
        # Tolerance for model stability check
        toll = 0.02

        # Flag for stability of the AR(2) model
        stable = 0
        output_noise_SD = np.inf
        while (~ stable) or (output_noise_SD > max_output_noise_SD):
            # Sample CGM error parameters
            cgm_error_parameters = np.random.multivariate_normal(mu, sigma)

            # Check the stability of the resulting AR(2) model
            stable = (cgm_error_parameters[5] >= -1) and (
                    cgm_error_parameters[5] <= (1 - np.abs(cgm_error_parameters[4]) - toll))

            # Compute the output noise standard deviation
            output_noise_SD = np.sqrt(cgm_error_parameters[6] ** 2 / (
                    1 - (cgm_error_parameters[4] ** 2) / (1 - cgm_error_parameters[5]) - cgm_error_parameters[5] * (
                    (cgm_error_parameters[4] ** 2) / (1 - cgm_error_parameters[5]) + cgm_error_parameters[5])))

        # Set the parameters of the CGM
        self.cgm_error_parameters = cgm_error_parameters
        self.output_noise_SD = output_noise_SD

        # Set memory terms
        self.ekm1 = 0
        self.ekm2 = 0

    def measure(self, IG, t):
        """
        Function that provides a CGM measure using the model of Vettoretti et al., Sensors, 2019.

        Parameters
        ----------
        IG: float
            The interstitial glucose concentration at current time (mg/dl).
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

        # If the model is IG, just echo the IG value
        if self.model == 'IG':
            return IG

        # Apply calibration error
        IGs = (self.cgm_error_parameters[0] + self.cgm_error_parameters[1] * t + self.cgm_error_parameters[
            2] * (t ** 2)) * IG + self.cgm_error_parameters[3]

        # Generate noise
        z = np.random.normal(0, 1)
        u = self.cgm_error_parameters[6] * z
        e = u + self.cgm_error_parameters[4] * self.ekm1 + self.cgm_error_parameters[5] * self.ekm2

        # Update memory terms
        self.ekm2 = self.ekm1
        self.ekm1 = e

        # Get final CGM
        return IGs + e

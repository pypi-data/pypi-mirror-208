This code provides you the solution of the radiative transfer equation in a single layer pigmented plane parallel medium. Ray is incident from air to the coating. Coating is coated on a substrate. Substrate could be air or other material such as silver, glass etc. The code estimates spectral absorptance, spectral hemispherical reflectance and transmittance.The code can account for; (i) independent and dependent (dense medium) scattering. dependent scattering is handled by static structure factor(ii) boundary reflections (can calculate refraction angle between air and medium with k>0)(iii) effective medium theory while calculating boundary reflection (maxwell-garnett effective medium theory)(iv) absorptive medium (mie in absorbing medium and refraction at absorbing medium). 
The code can't account for; (i) coherent backscattering, (ii) plasmonic coupling, (iii) near field effects and (iv) polarization.
While calculating the scattering direction the code can use (i) henyey greenstein phase function or (ii) exact scattering phase function that is calculated by Mie theory.

Inputs:

% lambda thickness radius (and sigma if particles are polydisperse) should have the same unit [micrometer is used in examples]

lambda=0.5; %freespace wavelength of incident ray in unit length 
thickness=100;  %thickness of coating in unit length  
f_v=0.10; %particle volume fraction 0.01 corresponds to 1% 
polar_angle_deg=0; %incident angles. 0 = perpendicular to slab. 90 is parallel and should be avoided.

for monodisperse case:
radius=0.05; %radius of particle in unit length  
for polydisperse case
avg_radius=0.2; %radius of particle in unit length  
sigma = 0.0001; %standard deviation of the radius in unit length

%optical properties
n_medium = 1.33; %real refractive index of medium
k_medium = 0; %imaginary refractive index of medium
n_pigment=1.5; %real refractive index of particle
k_pigment=0; %imaginary refractive index of particle
n_substrat=1; %real refractive index of substrate
k_substrat=0; %imaginary refractive index of substrate

%numerical stability settings
photon_number=10^5; %number of rays that will be traced, higher the number more accurate the result
nang=20000; %discretization of scattering angle, for large size parameters (>100) should be high (>50000) 
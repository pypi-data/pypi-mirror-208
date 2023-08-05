def maxwell_garnett(f_v=None,n_pigment=None,k_pigment=None,n_medium=None,k_medium=None):

    import numpy as np
    ev_pigment_e_a_=n_pigment ** 2 - k_pigment ** 2
    ev_pigment_e_a__= n_pigment * k_pigment * 2
    ev_pigment_e_b_=n_medium ** 2 - k_medium ** 2
    ev_pigment_e_b__= n_medium * k_medium * 2
    e_b=ev_pigment_e_b_ - ev_pigment_e_b__ * 1j
    e_a=ev_pigment_e_a_ - ev_pigment_e_a__ * 1j
    e_mg=e_b*(e_a + 2*e_b + 2*f_v*(e_a - e_b)) / (e_a + 2 * e_b - f_v*(e_a - e_b))

    
    e_mg_=np.real(e_mg)
    e_mg__=- np.imag(e_mg)
    n_eff_m=np.sqrt(0.5*(e_mg_ + np.sqrt(e_mg_ ** 2 + e_mg__ ** 2)))
    k_eff_m=np.sqrt(0.5*(- e_mg_ + np.sqrt(e_mg_ ** 2 + e_mg__ ** 2)))
    return n_eff_m,k_eff_m

def fresnel(n2,k2,theta_1):
    from numpy import sin, sqrt, arctan
    temp=n2**2-k2**2-sin(theta_1)**2
    p_sq=0.5*(sqrt(temp**2+4*n2**2*k2**2)+temp)
    theta_2=arctan(sin(theta_1)/sqrt(p_sq))
    return theta_2
 

def scatter_hg(g=None,s_x=None,s_y=None,s_z=None):

    from numpy import sqrt, pi, cos
    from random import random

    if (g == 0):
        cos_theta=2*random() - 1
    else:
        if (g == 1):
            cos_theta=1
        else:
            carpan=(1 - g*g)/(1 - g + 2*g*random())
            cos_theta=(1 + g*g - carpan*carpan) / (2*g)
        
    sin_theta=sqrt(1 - cos_theta*cos_theta)
    phi=2*pi*random() 
    cos_phi=cos(phi)
    if phi < pi:
        sin_phi= sqrt(1-cos_phi*cos_phi)
    else:
        sin_phi=- sqrt(1-cos_phi*cos_phi)
    
    
    if (s_z == 1):
        s_x_= sin_theta*cos_phi
        s_y_= sin_theta*sin_phi
        s_z_= cos_theta
    else:
        if (s_z == - 1):
            s_x_ = sin_theta*cos_phi;
            s_y_ = sin_theta*sin_phi;
            s_z_ = -cos_theta; 
        else:
            denom = sqrt(1 - s_z*s_z)
            s_x_ = sin_theta*(s_x * s_z * cos_phi - s_y * sin_phi) / denom + s_x * cos_theta
            s_y_ = sin_theta*(s_y * s_z * cos_phi + s_x * sin_phi) / denom + s_y * cos_theta
            s_z_ = -denom*sin_theta*cos_phi + s_z*cos_theta;
    
    return s_x_,s_y_,s_z_

def scatter_mc(cos_theta=None,s_x=None,s_y=None,s_z=None):
    
    from random import random
    from numpy import sqrt, pi, cos
    
    sin_theta=sqrt(1 - cos_theta*cos_theta)
    R_azimuth=random()
    phi=2*pi*R_azimuth
    cos_phi=cos(phi)
    
    if phi < pi:
        sin_phi=sqrt(1 - cos_phi*cos_phi)
    else:
        sin_phi=- sqrt(1 - cos_phi*cos_phi)
    
    
    if (s_z == 1):
        s_x_=sin_theta*cos_phi
        s_y_=sin_theta*sin_phi
        s_z_=cos_theta
    else:
        if (s_z == - 1):
            s_x_ = sin_theta*cos_phi
            s_y_ = sin_theta*sin_phi
            s_z_ = - cos_theta
        else:
            denom = sqrt(1 - s_z*s_z)
            s_x_ = sin_theta*(s_x * s_z * cos_phi - s_y * sin_phi) / denom + s_x * cos_theta
            s_y_ = sin_theta*(s_y * s_z * cos_phi + s_x * sin_phi) / denom + s_y * cos_theta
            s_z_ = -denom*sin_theta*cos_phi + s_z*cos_theta
    
    return s_x_,s_y_,s_z_

def snell(s_z=None,n_medium=None,k_medium=None,n_subs=None,k_subs=None):

    from random import random
    from numpy import sqrt, conj, real
    # n_medium,k_medium,n_subs,k_subs
    cos_teta=abs(s_z)
    if (s_z > 0):
        n_outside=n_subs
        k_outside=k_subs
    else:
        n_outside=1
        k_outside=0
    
    if (n_outside == n_medium and k_outside == k_medium):
        reflectance=0
    else:
        if (cos_teta > 0.9999):
            reflectance=((n_medium - n_outside) ** 2 + (k_medium - k_outside) ** 2) / ((n_medium + n_outside) ** 2 + (k_medium + k_outside) ** 2)
        else:
            if (cos_teta < (0.0001)):
                reflectance=1
            else:
                # general case radiative heat transfer howell 5th ed. page 741
                sin_teta=sqrt(1 - cos_teta*cos_teta)
                carpan2=(n_medium - 1j*k_medium) / (n_outside - 1j*k_outside)
                sin_x2=sin_teta*carpan2
                cos_x2=sqrt(1 - sin_x2*sin_x2)
                E_parallel=(cos_teta / cos_x2 - carpan2) / (cos_teta / cos_x2 + carpan2)
                R_parallel=E_parallel*conj(E_parallel)
                E_orth=- (cos_x2 / cos_teta - carpan2) / (cos_x2 / cos_teta + carpan2)
                R_orth=E_orth*conj(E_orth)
                reflectance=real(R_parallel + R_orth)*0.5
    
    Rastgele=random()
    if Rastgele > reflectance:
        #escape
        alive=0
    else:
        #trapped and reflect
        alive=1
    
    return alive

def abs_mie(radius=None,lambda_=None,n_medium=None,k_medium=None,n_pigment=None,k_pigment=None,nang=None):
    from numpy import sin, cos, arange, ceil, pi, dot, delete, sqrt, exp, imag, conj, real, finfo, trapz, zeros, linspace, arccos, multiply
    from scipy.special import jv,yv
    m1=n_medium + 1j*k_medium
    m2=n_pigment + 1j*k_pigment
    # Area=pi*radius^2;
    x0=2*pi*radius / lambda_
    
    mr = m2 / m1
    x = m1*x0
    y = m2*x0
    nmax=ceil(abs(x) + dot(4.05,abs(x) ** 0.3333) + 8.0)
    n=(arange(1,nmax+1))
    n_wide=arange(0,nmax + 2)
    nu=(n_wide + 0.5).T
    besselj_x=jv(nu,x)
    besselj_x_minus_1=besselj_x
    besselj_x_minus_1 = delete(besselj_x_minus_1, [-1, -2])
    besselj_x_plus_1=besselj_x
    besselj_x_plus_1 = delete(besselj_x_plus_1, [0, 1])
    besselj_x_middle=besselj_x
    besselj_x_middle= delete(besselj_x_middle, [0, -1])
    besselj_y=jv(nu,y)
    besselj_y_minus_1=besselj_y
    besselj_y_minus_1 = delete(besselj_y_minus_1, [-1, -2])
    besselj_y_plus_1=besselj_y
    besselj_y_plus_1 = delete(besselj_y_plus_1, [0, 1])
    besselj_y_middle=besselj_y
    besselj_y_middle= delete(besselj_y_middle, [0, -1])
    bessely_x=yv(nu,x)
    bessely_x_minus_1=bessely_x
    bessely_x_minus_1 = delete(bessely_x_minus_1, [-1, -2])
    bessely_x_plus_1=bessely_x
    bessely_x_plus_1 = delete(bessely_x_plus_1, [0, 1])
    bessely_x_middle=bessely_x
    bessely_x_middle= delete(bessely_x_middle, [0, -1])
    psi=sqrt(0.5*pi*x)*besselj_x_middle
    dpsi_chain_1=sqrt(0.5*pi*x)*0.5*(besselj_x_minus_1 - besselj_x_plus_1)
    dpsi_chain_2=0.25*pi*besselj_x_middle/sqrt(0.5*pi*x)
    psid=dpsi_chain_1 + dpsi_chain_2
    psi2=sqrt(0.5*pi*y)*besselj_y_middle
    dpsi_chain_1=sqrt(0.5*pi*y)*0.5*(besselj_y_minus_1 - besselj_y_plus_1)
    dpsi_chain_2=0.25*pi*besselj_y_middle/sqrt(0.5*pi*y)
    psi2d=dpsi_chain_1 + dpsi_chain_2
    xi=sqrt(0.5*pi*x)*bessely_x_middle
    dxi_chain_1=sqrt(0.5*pi*x)*0.5*(bessely_x_minus_1 - bessely_x_plus_1);
    dxi_chain_2=0.25*pi*bessely_x_middle/sqrt(0.5*pi*x);
    xid=dxi_chain_1 + dxi_chain_2
    xi=psi + xi*1j
    xid=psid + xid*1j
    ct=psi*psi2d
    ct2=psi2*psid
    # ct3 = mr*(psi.*xid - xi.*psid);
    ct4=mr*psi2*xid - xi*psi2d
    ct5=psi2*xid - mr*xi*psi2d
    an=(mr*ct2 - ct) / ct4
    bn=(ct2 - mr*ct) / ct5
    

    
    ########## calculate Q and C ##########
    S_FACTOR=exp(- imag(x))
    two_n_plus_1=1 + dot(2,(arange(1,nmax+1)).T)
    QS_FAR=dot(S_FACTOR ** 2,sum(multiply(two_n_plus_1,(abs(an) ** 2 + abs(bn) ** 2))))
    CQE= sum(two_n_plus_1*(conj(psi)*psid - psi*conj(psid) + bn*conj(psid)*xi + conj(bn)*psi*conj(xid) - an*conj(psi)*xid - conj(an)*conj(xi)*psid));
    CQS_NEAR=sum(two_n_plus_1*(-abs(an)**2*xid*conj(xi) + abs(bn)**2*xi*conj(xid)))
    Qabs=dot(- 2,imag((CQE - CQS_NEAR) / m1)) / (dot(dot(x0,x0),real(m1)))
    
    if Qabs < 0:
        Qabs=0
    if imag(x) < 10 ** - 6:
        QI = 1.0 + (4.0/3.0) * imag(x)
    else:
        QI = ((imag(x) - 0.5) * exp(2.0 * imag(x)) + 0.5 ) / ( imag(x) ** 2);
    Qsca_far=2*QS_FAR / abs(x)**2
    
    SCALE_FACTOR=exp(2*k_medium*x0)
    
    Qext_ind=(Qabs + Qsca_far) / QI
    w0_ind=Qsca_far / (Qabs + Qsca_far)
    
    ########## calculate g ##########
    nmax_int=nmax.astype('int')
    xt=0.0
    for i in range(1, nmax_int):
        xt = xt + (i*(i+2.0))/(i+1.0) * real(an[i-1]*conj(an[i]) + bn[i-1]*conj(bn[i])) + (2.0*i+1.0)/(i*(i+1.0)) * real(an[i-1]*conj(bn[i-1]));
    
    g_1=dot(2,xt)
    xt=0.0
    for i in range(1, nmax_int+1):
        xt = xt + (2*i+1)*(abs(an[i-1])**2 + abs(bn[i-1])**2);

    g_ind=g_1 / xt
    ########## calculate s1 and s2 ##########
    
    eps = finfo(float).eps
    theta=linspace(eps,pi,nang).T
    
    u=cos(theta)
    p=zeros((len(u),nmax_int+1))
    t=zeros((len(u),nmax_int+1))
    p[:,1]=1
    t[:,1]=u
    p[:,2]=dot(3,u)
    t[:,2]=dot(3,cos(dot(2,arccos(u))))
    for n1 in range(3, nmax_int):
        p[:,n1]=(multiply(multiply((dot(2,n1) - 1) / (n1 - 1),p[:,n1 - 1]),u)) - (multiply(n1 / (n1 - 1),p[:,n1 - 2]))
        t[:,n1]=multiply(dot(n1,u),p[:,n1]) - multiply((n1 + 1),p[:,n1 - 1])


    p = delete(p, 0, 1)
    t = delete(t, 0, 1)
    #n2=(dot(2,n) + 1) / (multiply(n,(n + 1)))
    n2=(2*n+1)/(n*(n+1))
    pin=n2*p
    tin=n2*t
    S1=(dot(an.T,pin.T) + dot(bn.T,tin.T))
    S2=(dot(an.T,tin.T) + dot(bn.T,pin.T))

    
    ########## mueller matrix ###############

    coeff=0.5*trapz((abs(S1)**2 + abs(S2)**2)*sin(theta),x=theta);
    P11_ind=(abs(S1) ** 2 + abs(S2) ** 2) / coeff

    # mm(:,2) = (abs(s2).^2 - abs(s1).^2)/2;
    # ct = s1 .* conj(s2);
    # mm(:,3)=real(ct);
    # mm(:,4)=imag(ct);
    return Qext_ind,w0_ind,g_ind,S1,S2,P11_ind,QI,S_FACTOR,SCALE_FACTOR

def SSF_correction(f_v=None,theta=None,lamda=None,r=None):
    from numpy import pi, sin, cos, dot, zeros
    S=zeros((len(theta)))
    for i1 in range(0, len(theta)):
        q=4 * pi * sin(theta[i1] / 2) / lamda
        x=q*r
        psi=sin(x) / x
        sigma=3*(sin(x) / x ** 3 - cos(x) / x ** 2)
        alpha=dot(f_v / (1 - f_v),(dot((1 + dot(3,f_v) / (1 - f_v)),sigma) + dot(3,psi))) + cos(x)
        beta=dot(dot(f_v / (1 - f_v),x),sigma) + sin(x)
        S[i1]=1 / (alpha ** 2 + beta ** 2)
    return S

def monte_carlo(photon_number=None,s_ref=None,cos_gecen=None,h=None,scat_prob=None,mu_tot=None,n_medium=None,k_medium=None,n_subs=None,k_subs=None,inv_cdf_cos=None,g=None,exact_scattering_phase=None):
    from numpy import sqrt, log, ceil
    from random import random
    if exact_scattering_phase:
        n_cdf_random=inv_cdf_cos.size
    r_tot,t_tot,a_tot=0,0,0
    for i in range(photon_number):
        r_no,t_no,a_no,x,y,z,s_x,Rastgele=0,0,0,0,0,0,0,random()
    
        if Rastgele > s_ref:
            #ray penetrates to the medium
            alive=1
        else:
            #specular reflection
            alive,r_no=0,1
        s_y=sqrt(1 - cos_gecen*cos_gecen)
        s_z=cos_gecen
        l_beta=- log(random()) / mu_tot
        while alive:
            if (s_z > 0):
                l_w=(h - z) / s_z
            else:
                l_w=- z / s_z
            if l_w < l_beta:
                min_index=1
                min_l=l_w
            else:
                min_index=2
                min_l=l_beta
            x=x + min_l*s_x
            y=y + min_l*s_y
            z=z + min_l*s_z
            if (min_index == 1):
                alive=snell(s_z,n_medium,k_medium,n_subs,k_subs)
                if (alive == 0):
                    if s_z > 0:
                        if k_subs == 0:
                            t_no=1
                        else:
                            a_no=1
                    else:
                        r_no=1
                else:
                    l_beta=l_beta - l_w
                    s_z=- s_z
            else:
                random_no=random()
                if random_no < scat_prob:
                    if exact_scattering_phase:
                        cos_theta=inv_cdf_cos[ceil(random()*n_cdf_random).astype('int')-1]
                        s_x,s_y,s_z=scatter_mc(cos_theta,s_x,s_y,s_z)
                    else:
                        s_x,s_y,s_z=scatter_hg(g,s_x,s_y,s_z)
                        
                    l_beta= -log(random()) / mu_tot
                else:
                    alive=0
                    a_no=1

        r_tot=r_tot + r_no
        t_tot=t_tot + t_no
        a_tot=a_tot + a_no
    
    r_tot=r_tot / photon_number
    t_tot=t_tot / photon_number
    a_tot=a_tot / photon_number
    return r_tot,t_tot,a_tot

def rte_monodisperse(calculate_boundary_reflection=True,dependent_scattering=True,effective_medium=True,exact_scattering_phase=True,lambda_=0.5,thickness=100,radius=0.2,f_v=0.1,polar_angle_deg=0,n_medium=1.33,k_medium=0.0,n_pigment=1.5,k_pigment=0,n_substrat=1,k_substrat=0,photon_number=10**5, nang=10000):
    
    from numpy import sqrt, pi, conj, finfo, sin, cos, linspace, real, trapz, flip, zeros, interp
    
    #solution of radiative transfer equation in one layer pigmented plane parallel medium
    #ray is incident from air to coating. coating is coated on a substrate
    #substrate could be air or other material such as silver, glass etc.
    #the code estimates spectral hemispherical reflectance, transmittance and absorptance
    #can handle; independent and dependent scattering, boundary reflections, absorption in
    #medium. can't handle; coherent backscattering, plascmon coupling, near field effects and polarized ray tracing.
    #while calculating the scattering direction the code uses  henyey greenstein 

    
    ####################### end of inputs #############################
    
    eps = finfo(float).eps
    
    teta=linspace(eps,pi,nang)
    u=cos(teta)
    polar_angle_rad=polar_angle_deg*pi / 180
    
    
    if calculate_boundary_reflection:
        if effective_medium:
            n_eff_m,k_eff_m=maxwell_garnett(f_v,n_pigment,k_pigment,n_medium,k_medium)
        else:
            n_eff_m=n_medium
            k_eff_m=k_medium
        # calculate surface reflection from air to medium. 
        # medium to air and medium to substrate is calculated within snell.m.
        # air to medium is calculated here seperately since we need refraction angle
        teta_prime=fresnel(n_eff_m,k_eff_m,polar_angle_rad)
        cos_teta=cos(polar_angle_rad)
        sin_teta=sqrt(1 - cos_teta*cos_teta)
        carpan2=1 / (n_eff_m - 1j*k_eff_m)
        sin_x2=sin_teta*carpan2
        cos_x2=sqrt(1 - sin_x2*sin_x2)
        carpan1=cos_teta / cos_x2
        carpan3=cos_x2 / cos_teta
        E_parallel=(carpan1 - carpan2) / (carpan1 + carpan2)
        R_parallel=E_parallel*conj(E_parallel)
        E_orth=(carpan3 - carpan2) / (carpan3 + carpan2)
        R_orth=E_orth*conj(E_orth)
        reflectance=real(R_parallel + R_orth)*0.5
        sur_reflection=reflectance
    else:
        teta_prime=polar_angle_rad
        sur_reflection=0
        n_eff_m=1
        k_eff_m=0
        n_substrat=1
        k_substrat=0
    
    V=4*pi*radius ** 3 / 3
    Area=pi*radius ** 2
    x=2*pi*(n_medium + k_medium*1j)*radius / lambda_
    
    if abs(x) > 0.2 and effective_medium:
       print('Effective medium theory is enabled but size parameter is larger than 0.2')
    
    
    Qext_ind,w0_ind,g_ind,S1,S2,P11_ind,QI,S_FACTOR,SCALE_FACTOR=abs_mie(radius,lambda_,n_medium,k_medium,n_pigment,k_pigment,nang)
    
    S11=S_FACTOR ** 2*0.5*(abs(S1) ** 2 + abs(S2) ** 2) / QI
    Qsca_ind= Qext_ind * w0_ind
    Qabs=Qext_ind*(1 - w0_ind)
    if dependent_scattering:
        S=SSF_correction(f_v,teta,lambda_ / abs(n_medium + k_medium*1j),radius)
        Qsca=2*trapz(sin(teta)*S11*S,x=teta) / abs(x) ** 2
        g=trapz(sin(teta)*cos(teta)*S11*S,x=teta) / trapz(sin(teta)*S11*S,x=teta)
        if exact_scattering_phase:
            P11=S11*S / trapz(S11*sin(teta)*S,x=teta)
    else:
        Qsca=Qsca_ind
        g=g_ind
        if exact_scattering_phase:
            P11=S11 / trapz(sin(teta)*S11,x=teta)
    
    
    if exact_scattering_phase:
        flipped_u=flip(u)
        zero_to_one=linspace(0,1,nang).T
        cdf=zeros((nang))
        for i in range(nang):
            cdf[i]=trapz(P11[0:i+1],x=flipped_u[0:i+1])
        inv_cdf_cos=cos(interp(zero_to_one,cdf,teta))
        ### when inv_cdf_cos(end) is not -1 it means nang is not high enough
        if S11.size>0:
            if inv_cdf_cos[-2] > - 0.99:
                print('consider to increase nang value')
        ### end of warning
    else:
        inv_cdf_cos=0.0
    
    
    Csca=Area*Qsca
    Cabs=Area*Qabs
    alfa=f_v*Csca / V
    beta=f_v*Cabs / V + (1 - f_v)*4*pi*k_medium / lambda_
    mu_tot=alfa + beta
    scat_prob=alfa / mu_tot
    
    ref_nh,tra_nh,absorptance=monte_carlo(photon_number,sur_reflection,cos(teta_prime),thickness,scat_prob,mu_tot,n_eff_m,k_eff_m,n_substrat,k_substrat,inv_cdf_cos,g,exact_scattering_phase)
    
    return ref_nh,tra_nh,absorptance

def rte_polydisperse(calculate_boundary_reflection=True,dependent_scattering=True,effective_medium=True,exact_scattering_phase=True,lambda_=0.5,thickness=100,avg_radius=0.2,sigma=0.01,f_v=0.1,polar_angle_deg=0,n_medium=1.33,k_medium=0.0,n_pigment=1.5,k_pigment=0,n_substrat=1,k_substrat=0,photon_number=10**5, nang=10000, no_of_r=20):

    from numpy import sqrt, pi, conj, finfo, sin, cos, linspace, real, trapz, flip, zeros, interp
    from scipy.stats import norm
    eps = finfo(float).eps
    rad_list=linspace(avg_radius - sigma*3,avg_radius + sigma*3,no_of_r)
    rad_list[rad_list <= 0]=[]
    weight_vector=norm.pdf(rad_list, avg_radius, sigma)
    normalize_weight_vector=trapz(weight_vector, x=rad_list)
    weight_vector=weight_vector / normalize_weight_vector
    
    teta=linspace(eps,pi,nang)
    u=cos(teta)
    polar_angle_rad=polar_angle_deg*pi / 180
    
    P11_r=zeros((rad_list.size,nang))
    Csca_r=zeros((rad_list.size))
    Cabs_r=zeros((rad_list.size))
    g_r=zeros((rad_list.size))
    
    if calculate_boundary_reflection:
        if effective_medium:
            n_eff_m,k_eff_m=maxwell_garnett(f_v,n_pigment,k_pigment,n_medium,k_medium)
        else:
            n_eff_m=n_medium
            k_eff_m=k_medium
        # calculate surface reflection from air to medium. 
        # medium to air and medium to substrate is calculated within snell.m.
        # air to medium is calculated here seperately since we need refraction angle
        teta_prime=fresnel(n_eff_m,k_eff_m,polar_angle_rad)
        cos_teta=cos(polar_angle_rad)
        sin_teta=sqrt(1 - cos_teta*cos_teta)
        carpan2=1 / (n_eff_m - 1j*k_eff_m)
        sin_x2=sin_teta*carpan2
        cos_x2=sqrt(1 - sin_x2*sin_x2)
        carpan1=cos_teta / cos_x2
        carpan3=cos_x2 / cos_teta
        E_parallel=(carpan1 - carpan2) / (carpan1 + carpan2)
        R_parallel=E_parallel*conj(E_parallel)
        E_orth=(carpan3 - carpan2) / (carpan3 + carpan2)
        R_orth=E_orth*conj(E_orth)
        reflectance=real(R_parallel + R_orth)*0.5
        sur_reflection=reflectance
    else:
        teta_prime=polar_angle_rad
        sur_reflection=0
        n_eff_m=1
        k_eff_m=0
        n_substrat=1
        k_substrat=0
    
    for i in range(rad_list.size):
        radius=rad_list[i]
        Area=pi*radius ** 2
        x=2*pi*(n_medium + k_medium*1j)*radius / lambda_
        if abs(x) > 0.2 and effective_medium:
            print('Effective medium theory is enabled but size parameter is larger than 0.2')
        Qext_ind,w0_ind,g_ind,S1,S2,P11_ind,QI,S_FACTOR,SCALE_FACTOR=abs_mie(radius,lambda_,n_medium,k_medium,n_pigment,k_pigment,nang)
    
        S11=S_FACTOR ** 2*0.5*(abs(S1) ** 2 + abs(S2) ** 2) / QI
        Qsca_ind= Qext_ind * w0_ind
        Qabs=Qext_ind*(1 - w0_ind)
        if dependent_scattering:
            S=SSF_correction(f_v,teta,lambda_ / abs(n_medium + k_medium*1j),radius)
            Qsca=2*trapz(sin(teta)*S11*S,x=teta) / abs(x) ** 2
            g=trapz(sin(teta)*cos(teta)*S11*S,x=teta) / trapz(sin(teta)*S11*S,x=teta)
            if exact_scattering_phase:
                P11_r[i][:]=S11*S / trapz(S11*sin(teta)*S,x=teta)
        else:
            Qsca=Qsca_ind
            g=g_ind
            if exact_scattering_phase:
                P11_r[i][:]=S11 / trapz(sin(teta)*S11,x=teta)
        Csca_r[i]=Area*Qsca
        Cabs_r[i]=Area*Qabs
        g_r[i]=g
    
    Csca=trapz(Csca_r*weight_vector,x=rad_list)
    Cabs=trapz(Cabs_r*weight_vector,x=rad_list)
    P11=trapz((Csca_r*weight_vector)*P11_r.T,x=rad_list) / trapz(Csca_r*weight_vector,x=rad_list)
    g=trapz(g_r*Csca_r*weight_vector,x=rad_list) / trapz(Csca_r*weight_vector,x=rad_list)
    
    if exact_scattering_phase:
        flipped_u=flip(u)
        zero_to_one=linspace(0,1,nang).T
        cdf=zeros((nang))
        for i in range(nang):
            cdf[i]=trapz(P11[0:i+1],x=flipped_u[0:i+1])
        inv_cdf_cos=cos(interp(zero_to_one,cdf,teta))
        ### when inv_cdf_cos(end) is not -1 it means nang is not high enough
        if S11.size>0:
            if inv_cdf_cos[-2] > - 0.99:
                print('consider to increase nang value')
        ### end of warning
    else:
        inv_cdf_cos=0
    
    r_3=trapz(weight_vector*rad_list ** 3,x = rad_list)
    V_avg= (4 / 3) * pi * r_3
    alfa=f_v * Csca / V_avg
    beta=f_v*Cabs / V_avg + (1 - f_v)*4*pi*k_medium / lambda_
    
    mu_tot=alfa + beta
    scat_prob=alfa / mu_tot
    ref_nh,tra_nh,absorptance=monte_carlo(photon_number,sur_reflection,cos(teta_prime),thickness,scat_prob,mu_tot,n_eff_m,k_eff_m,n_substrat,k_substrat,inv_cdf_cos,g,exact_scattering_phase)

    return ref_nh,tra_nh,absorptance
from __future__ import division

import healpy as hp
import numpy as np
import _flib as flib
import os
from astropy.io import fits
import logging

__all__ = ['Xpol','Xcov','Bins','fsky','Xpol_Wrapper','apodization','sample_variance','listcross','fit_dipole']

log = logging.getLogger("healpy")


def fsky(mask):
    """
    Return sky fraction as fsky = <m^2>**2 / <m^4> 
    """
    return np.mean(mask**2)**2/np.mean(mask**4)

def apodization( mask, deg, threshold=1e-5, method="Gaussian"):
    log.setLevel(logging.INFO)
    
    if method == "Gaussian":
        smask = hp.smoothing( mask, fwhm=np.deg2rad(deg))
        smask[smask < (0. + threshold)] = 0.+ threshold
        smask[smask > (1. - threshold)] = 1.- threshold
    else:
        print( "Method allowed: Gaussian")
        return
    return smask


def sample_variance( l, cl, fsky=1.):
    """
    Compute sample variance for a given sky fraction

    Inputs:
        l: array of multipoles values
        cl: 2darray of power spectrum values (can be any length but order should be TT,EE,BB,TE,TB,EB)

    Optional:
        fsky: sky fraction (default=1)

    Output:
        array of cosmic variance
    """
    acl = np.asarray( cl)
    cosmic = 2./(2*l+1)/fsky * acl*acl
    cosmic[3] = (acl[0]*acl[1]+acl[3]*acl[3])/(2*l+1)/fsky
    if len(cl) > 4:
        cosmic[4] = (acl[0]*acl[2]+acl[4]*acl[4])/(2*l+1)/fsky
    if len(cl) > 5:
        cosmic[5] = (acl[1]*acl[2]+acl[5]*acl[5])/(2*l+1)/fsky

    return cosmic

def listcross( listmap, auto=False):
    import itertools
    if auto:
        return list(itertools.combinations_with_replacement(listmap,2))
    else:
        return list(itertools.combinations(listmap,2))


class Bins(object):
    """
        lmins : list of integers
            Lower bound of the bins
        lmaxs : list of integers
            Upper bound of the bins (not included)
    """
    def __init__( self, lmins, lmaxs):
        if not(len(lmins) == len(lmaxs)):
            raise ValueError('Incoherent inputs')

        lmins = np.asarray( lmins)
        lmaxs = np.asarray( lmaxs)
        cutfirst = np.logical_and(lmaxs>=2 ,lmins>=2)
        self.lmins = lmins[cutfirst]
        self.lmaxs = lmaxs[cutfirst]
        
        self._derive_ext()
    
    @classmethod
    def fromdeltal( cls, lmin, lmax, delta_ell):
        nbins = (lmax - lmin + 1) // delta_ell
        lmins = lmin + np.arange(nbins) * delta_ell
        lmaxs = lmins + delta_ell
        return cls( lmins, lmaxs)

    def _derive_ext( self):
        self.lmin = min(self.lmins)
        self.lmax = max(self.lmaxs)-1
        if self.lmin < 1:
            raise ValueError('Input lmin is less than 1.')
        if self.lmax < self.lmin:
            raise ValueError('Input lmax is less than lmin.')
        
        self.nbins = len(self.lmins)
        self.lbin = (self.lmins + self.lmaxs - 1) / 2
        self.dl   = (self.lmaxs - self.lmins)

    def bins(self):
        return self.lmins, self.lmaxs
    
    def cut_binning(self, lmin, lmax):
        sel = np.where( (self.lmins >= lmin) & (self.lmaxs <= lmax+1) )[0]
        self.lmins = self.lmins[sel]
        self.lmaxs = self.lmaxs[sel]
        self._derive_ext()
    
    def _bin_operators(self,Dl=False):
        if Dl:
            ell2 = np.arange(self.lmax+1)
            ell2 = ell2 * (ell2 + 1) / (2 * np.pi)
        else:
            ell2 = np.ones(self.lmax+1)
        p = np.zeros((self.nbins, self.lmax+1))
        q = np.zeros((self.lmax+1, self.nbins))
        
        for b, (a, z) in enumerate(zip(self.lmins, self.lmaxs)):
            p[b, a:z] = ell2[a:z] / (z - a)
            q[a:z, b] = 1 / ell2[a:z]
        
        return p, q
    
    def bin_spectra(self, spectra, Dl=False):
        """
        Average spectra in bins specified by lmin, lmax and delta_ell,
        weighted by `l(l+1)/2pi`.
        Return Cb
        """
        spectra = np.asarray(spectra)
        minlmax = min([spectra.shape[-1] - 1,self.lmax])
#        if Dl:
#            fact_binned = (self.lbin * (self.lbin + 1)) / (2 * np.pi)
#        else:
#            fact_binned = 1.
        
        _p, _q = self._bin_operators(Dl=Dl)
        return np.dot(spectra[..., :minlmax+1], _p.T[:minlmax+1,...]) #* fact_binned





class Xpol(object):
    """
    (Cross-) power spectra estimation using the Xpol method.
    Hinshaw et al. 2003, Tristram et al. 2005.

    Example
    -------
    import xpol
    binning = xpol.Bins( lmins, lmaxs)
    xp = xpol.Xpol(mask, bins=binning)
    pcl,cl = xp.get_spectra( dT, Dl=True)
    pcl12,cl12 = xp.get_spectra( dT1, dT2, Dl=True)

    """
    def __init__(self, mask, mask2=None, bins=None, polar=True, verbose=False, wlmax=None, Dl=False):
        """
        Inputs
        ------
            mask: array, weighting mask to apply on data, (2,npix) if polar=True

        Options
        -------
            bins: Class Bins, binning scheme
            mask2: array, weighting mask to apply on the second map (for cross-correlation), (2,npix) if polar=True
            polar: boolean, polarisation computation
            verbose: boolean
            Dl: boolean, outputs in l(l+2)/2pi Cl
        """

        if bins is None:
            bins = Bins.fromdeltal(2,3*self.nside-1,1)
        self.lmin = int(bins.lmin)
        self.lmax = int(bins.lmax)
        self.verbose = verbose
        self.polar = polar

        mask = np.asarray(mask)
        if self.polar:
            if mask.ndim != 2:
                raise ValueError("Need 2-dim mask array if polar.")
        else:
            if mask.ndim == 1:
                mask = mask.reshape( -1, len(mask))

        self.npix = np.shape(mask)[-1]
        self.nside = hp.npix2nside(self.npix)
        if self.lmax > 3*self.nside-1:
            raise ValueError("Input lmax is too high for resolution.")

        if verbose:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
        
        if self.verbose: print( "\tCompute bin operators")
        self._p, self._q = bins._bin_operators(Dl=Dl)
        self.lbin = bins.lbin
        self.bin_spectra = bins.bin_spectra
        
        #compute cross-spectrum of weight mask
        if self.verbose: print( "\talm2map mask")
        if wlmax is None:
            wlmax = self.lmax ###3*self.nside-1

        return
    
        wlTP = None
        wlPT = None
        wlPP = None
        if mask2 is None:
            if polar:
                self.mask1 = self.mask2 = np.array([mask[0],mask[1],mask[1]])
                wlTP = wlPT = hp.anafast( mask1[0], mask1[1], lmax=wlmax)
                wlPP = hp.anafast( mask1[1], lmax=wlmax)
            else:
                self.mask1 = self.mask2 = mask.reshape(-1,self.npix)
            wlTT = hp.anafast(self.mask1[0],lmax=wlmax)
        else:
            mask2 = np.asarray(mask2)
            if self.polar:
                if mask2.ndim != 2:
                    raise ValueError("Need 2-dim mask array if polar.")
                self.mask1 = np.array([mask[0],mask[1],mask[1]])
                self.mask2 = np.array([mask2[0],mask2[1],mask2[1]])
                wlTP = hp.anafast( self.mask1[0], self.mask2[1], lmax=wlmax)
                wlPT = hp.anafast( self.mask1[1], self.mask2[0], lmax=wlmax)
                wlPP = hp.anafast( self.mask1[1], self.mask2[1], lmax=wlmax)
            else:
                self.mask1 = mask1.reshape( -1, self.npix)
                self.mask2 = mask2.reshape( -1, self.npix)
            wlTT = hp.anafast( self.mask1[0], self.mask2[0], lmax=wlmax)
        
        #compute coupling kernels for covariance
        if self.verbose: print( "\tCompute coupling kernels Mll")
        mll_binned = self._get_Mbb( wlTT, wlTP, wlPT, wlPP)

        if self.verbose: print( "\tInverse Mll")
        self.mll_binned_inv = self._inv_mll(mll_binned)

    def get_spectra(self, m1, m2=None, bell=None, bell1=None, bell2=None, pixwin=True, Dl=False, remove_dipole=True, iter=3):
        """
        Return biased and Xpol-debiased estimations of the power spectra of
        a Healpix map or of the cross-power spectra if *map2* is provided.
        
        bins = Bins.fromdeltal( lmin, lmax, deltal)
        xpol = Xpol(mask, bins)
        biased, unbiased = xpol.get_spectra(map1, [map2])

        The unbiased Cls are binned. The number of bins is given by
        (lmax - lmin) // delta_ell, using the values specified in the Xpol's
        object initialisation. As a consequence, the upper bound of the highest
        l bin may be less than lmax. The central value of the bins can be
        obtained through the attribute `xpol.lbin`.

        Parameters
        ----------
        map1 : Nx3 or 3xN array
            The I, Q, U Healpix maps.
        map2 : Nx3 or 3xN array, optional
            The I, Q, U Healpix maps.

        Returns
        -------
        biased : float array of shape (9, lmax+1)
            The anafast's pseudo (cross-) power spectra for TT,EE,BB,TE,TB,EB,ET,BT,BE.
            The corresponding l values are given by `np.arange(lmax + 1)`.

        unbiased : float array of shape (9, nbins)
            The Xpol's (cross-) power spectra for TT,EE,BB,TE,TB,EB,ET,BT,BE.
            The corresponding l values are given by `xpol.lbin`.
        """
        cross = m2 is not None
        npix = hp.nside2npix(self.nside)
        
        #Map1
        if self.verbose:
            if cross:
                print( "\tCompute alms map1")
            else:
                print( "\tCompute alms")
        map1 = np.array(m1)
        if map1.shape[-1] == 3:
            map1 = map1.T
        map1 = map1.reshape(-1,npix)
        self._removeUndef(map1)
        if remove_dipole: self._remove_dipole( map1[0], self.mask1[0], bad=0.)
        alms1 = hp.map2alm(map1*self.mask1, pol=self.polar, lmax=self.lmax, iter=iter)
        del(map1)
        
        #Map2
        if cross:
            if self.verbose: print( "\tCompute alms map2")
            map2 = np.array(m2)
            if map2.shape[-1] == 3:
                map2 = map2.T
            map2 = map2.reshape(-1,npix)
            self._removeUndef(map2)
            if remove_dipole: self._remove_dipole( map2[0], self.mask2[0], bad=0.)
            alms2 = hp.map2alm( map2*self.mask2, pol=self.polar, lmax=self.lmax, iter=iter)
            del(map2)
        else:
            alms2 = alms1

        #alm2cl
        if self.verbose: print( "\tAlms 2 cl")
        biased = hp.alm2cl( alms1, alms2, lmax=self.lmax) #healpy order (TT,EE,BB,TE,EB,TB)
        if self.polar:
            biased = biased[[0,1,2,3,5,4]] #swith TB and EB
            if cross:
                biased21 = hp.alm2cl( alms2, alms1, lmax=self.lmax)
                biased21 = biased21[[0,1,2,3,5,4]] #swith TB and EB
                biased = np.array( np.concatenate( (biased, biased21[[3,4,5]]))) #concatenate with alms2xalms1
        del( alms1)
        del( alms2)
        
        #beam function
        if self.verbose: print( "\tCorrect beams")
        if bell is not None:
            bl = bell[:self.lmax+1]**2
        else:
            bl = np.ones(self.lmax+1)
        if bell1 is not None:
            if bell2 is None:
                bell2 = bell1
            bl *= bell1[:self.lmax+1]*bell2[:self.lmax+1]
        if pixwin:
            bl *= hp.pixwin(self.nside)[:self.lmax+1]**2
        
        #bin spectra
        if self.verbose: print( "\tBin spectrum")
        binned = self.bin_spectra(biased,Dl=Dl)
        
        #debias
        if self.verbose: print( "\tDebias spectra")
        unbiased = self._debias_spectra( binned)
        unbiased /= self.bin_spectra(bl,Dl=False)
        
        return biased, unbiased

    def _debias_spectra(self, binned):
        cross = len(binned) == 9
        
        if self.polar:
            TT_TT, EE_EE, EE_BB, TE_TE, ET_ET = self.mll_binned_inv
        else:
            TT_TT = self.mll_binned_inv
        
        n = len(TT_TT)
        if self.polar is False:
            TT = np.dot( TT_TT, binned)
            return np.asarray(TT)

        #TT block
        TT = np.dot( TT_TT, binned[0])

        ##EE-BB block
        out = np.zeros( (2*n,2*n) )
        out[0*n:1*n, 0*n:1*n] = EE_EE
        out[1*n:2*n, 1*n:2*n] = EE_EE
        out[0*n:1*n, 1*n:2*n] = EE_BB
        out[1*n:2*n, 0*n:1*n] = EE_BB
        vec = np.dot( out, binned[1:3].ravel())
        EE = vec[0:n]
        BB = vec[n:]

        #TE, TB blocks
        TE = np.dot( TE_TE, binned[3])
        TB = np.dot( TE_TE, binned[4])
        if cross:
            ET = np.dot( ET_ET, binned[6])
            BT = np.dot( ET_ET, binned[7])
        
        #EB-BE block
        if cross:
            out[0*n:1*n, 0*n:1*n] = EE_EE
            out[1*n:2*n, 1*n:2*n] = EE_EE
            out[0*n:1*n, 1*n:2*n] = -EE_BB
            out[1*n:2*n, 0*n:1*n] = -EE_BB
            vec = np.dot( out, binned[[5,8]].ravel())
            EB = vec[0:n]
            BE = vec[n:]
        else:
            EB = np.dot( EE_EE, binned[5])

        if cross:
            spec = [TT,EE,BB,TE,TB,EB,ET,BT,BE]
        else:
            spec = [TT,EE,BB,TE,TB,EB]

        return spec

    def _replaceUndefWith0(self,mymap):
        badpix = np.isclose( mymap,hp.UNSEEN)
        mymap[badpix] = 0.

    def _removeUndef(self,mymap):
        for m in mymap:
            self._replaceUndefWith0( m)

    def _remove_dipole(self, m, mask, bad=hp.UNSEEN):
        npix = m.size
        nside = hp.npix2nside(npix)
        bunchsize = npix // 24 if nside > 128 else npix

        #fit dipole where mask != 0
        mono, dipole = hp.fit_dipole(m*(mask>0), bad=0.)

        #remove dipole
        for ibunch in range(npix // bunchsize):
            ipix = np.arange(ibunch * bunchsize, (ibunch + 1) * bunchsize)
            ipix = ipix[(m.flat[ipix] != bad) & (np.isfinite(m.flat[ipix]))]
            x, y, z = hp.pix2vec(nside, ipix)
            m.flat[ipix] -= mono
            m.flat[ipix] -= dipole[0] * x
            m.flat[ipix] -= dipole[1] * y
            m.flat[ipix] -= dipole[2] * z

    def _inv_mll(self, mll_binned):
        if self.polar:
            TT_TT, EE_EE, EE_BB, TE_TE, ET_ET = mll_binned
        else:
            TT_TT = mll_binned

        n = len(TT_TT)
        TT_TT = np.linalg.inv(TT_TT)
        if self.polar is False:
            return TT_TT
        
        TE_TE = np.linalg.inv(TE_TE)
        ET_ET = np.linalg.inv(ET_ET)
        out = np.zeros( (2*n,2*n) )
        out[0*n:1*n, 0*n:1*n] = EE_EE
        out[1*n:2*n, 1*n:2*n] = EE_EE
        out[0*n:1*n, 1*n:2*n] = EE_BB
        out[1*n:2*n, 0*n:1*n] = EE_BB
        out = np.linalg.inv(out)
        EE_EE = out[0*n:1*n, 0*n:1*n]
        EE_BB = out[0*n:1*n, 1*n:2*n]
        
        return TT_TT, EE_EE, EE_BB, TE_TE, ET_ET

    def _get_Mll_blocks(self, wlTT, wlTP, wlPT, wlPP):
        if self.polar:
            TT_TT, EE_EE, EE_BB, TE_TE, ET_ET, ier = flib.xpol.mll_blocks_pol(self.lmax, wlTT, wlTP, wlPT, wlPP)
        else:
            TT_TT, ier = flib.xpol.mll_blocks(self.lmax, wlTT)
        if ier > 0:
            msg = ['Either L2 < ABS(M2) or L3 < ABS(M3).',
                   'Either L2+ABS(M2) or L3+ABS(M3) non-integer.'
                   'L1MAX-L1MIN not an integer.',
                   'L1MAX less than L1MIN.',
                   'NDIM less than L1MAX-L1MIN+1.'][ier-1]
            raise RuntimeError(msg)

        if self.polar:
            return TT_TT, EE_EE, EE_BB, TE_TE, ET_ET
        else:
            return TT_TT

    def _get_Mbb(self, wlTT, wlTP, wlPT, wlPP):
        if self.polar:
            TT_TT, EE_EE, EE_BB, TE_TE, ET_ET = self._get_Mll_blocks( wlTT, wlTP, wlPT, wlPP)
        else:
            TT_TT = self._get_Mll_blocks( wlTT, wlTP, wlPT, wlPP)

        n = len(self.lbin)
        
        TT_TT = self._p @ TT_TT @ self._q
        if self.polar is False:
            return TT_TT
        
        EE_EE = self._p @ EE_EE @ self._q
        EE_BB = self._p @ EE_BB @ self._q
        TE_TE = self._p @ TE_TE @ self._q
        ET_ET = self._p @ ET_ET @ self._q
        
        return TT_TT, EE_EE, EE_BB, TE_TE, ET_ET



class Xcov(Xpol):
    """
    (Cross-) power spectra covariance matrix estimation.
    Tristram et al. 2005, MNRAS 358, 3
    Couchot et al. 2017, A&A 602, A41

    Compute cross-spectra covariance block for <AB,CD>

    Example
    -------
    import xpol
    binning = xpol.Bins( lmins, lmaxs)
    xp = xpol.Xcov(maskA, , maskB, bins=binning)
    clcov = xc.get_clcov_blocks( clAC, clBD, clAD, clBC)
    
    """
    def __init__(self, maskA, maskB=None, maskC=None, maskD=None, bins=None, polar=True, verbose=False, wlmax=None):
        """
        Inputs
        ------
            maskA: array, weighting mask to apply on mapA
        
        Options
        -------
            maskB: array, weighting mask to apply on mapB
            maskC: array, weighting mask to apply on mapC
            maskD: array, weighting mask to apply on mapD
            bins: Class Bins, binning scheme
            polar: boolean, polarisation computation [default=True]
            verbose: boolean [default=False]
        
        """

        if verbose:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)

        #compute Mll mixing kernels
        if verbose: print( "Compute kernel AB")
        Xpol.__init__( self, maskA, mask2=maskB, bins=bins, polar=polar, verbose=False, Dl=False)
        self.invmll_AB = np.copy(self.mll_binned_inv)
        if maskC is None:
            self.invmll_CD = self.invmll_AB
        else:
            if verbose: print( "Compute kernel CD")
            Xpol.__init__( self, maskC, mask2=maskD, bins=bins, polar=polar, verbose=False, Dl=False)
            self.invmll_CD = np.copy(self.mll_binned_inv)
        
        self.dl = bins.dl
        
        #compute coupling kernels for covariance
        if wlmax is None:
            wlmax = bins.lmax

        #only one mask
        if maskB is None:
            if self.verbose: print( "\tCompute covariance kernels ")
            wl = hp.anafast(maskA*maskA,lmax=wlmax)
            self.mll_ACBD = self.mll_ADBC = self._get_Mbb( wl)
            return

        #same masks for cross-spectra for A=C and B=D
        if maskC is None:
            maskC = maskA
            maskD = maskB
        if maskD is None: maskD = maskC 
        
        if verbose: print( "\tCompute covariance kernel AC-BD")
        wl = hp.anafast(maskA*maskC,map2=maskB*maskD,lmax=wlmax)
        self.mll_ACBD = self._get_Mbb( wl)
        if verbose: print( "\tCompute covariance kernel AD-BC")
        wl = hp.anafast(maskA*maskD,map2=maskB*maskC,lmax=wlmax)
        self.mll_ADBC = self._get_Mbb( wl)
        return

    def _smooth_cl( self, cl, lcut=0, nsm=2):
        import scipy.ndimage as nd

        if nsm == 0:
            return(cl)
        
        #gauss filter
        if lcut < 2*nsm:
            shift=0
        else:
            shift=2*nsm

        scl = np.copy(cl)
        data = nd.gaussian_filter1d( cl[max(0,lcut-shift):], nsm)
        scl[lcut:] = data[shift:]
        
        return scl

    def _get_pcl_cov(self, clAC, clBD, clAD, clBC):
        """
        Compute covariance matrix for pseudo-spectra <AB,CD>
        
        inputs:
            cl: 2d array (ntag,nbin)
                [TT,EE,BB,TE,TB,EB,ET,BT,BE]

        output:
            out: 2d array (5*nbin,5*nbin)
                 [TT,EE,BB,TE,ET]
        """
        n = len(self.lbin)
        ndim = 5*n if self.polar else n
        out = np.zeros((ndim, ndim))
        nu_l = (2.*self.lbin+1.) * self.dl
        
        #symmetrization
        tags = dict( zip( ["TT","EE","BB","TE","ET"], [0,1,2,3,6]))
        symcl = lambda cl,t: np.add.outer(cl[tags[t]],cl[tags[t]])/2.

        if self.polar:
            s00_ACBD, sPP_ACBD, sMM_ACBD, s0P_ACBD = self.mll_ACBD
            s00_ADBC, sPP_ADBC, sMM_ADBC, s0P_ADBC = self.mll_ADBC
        else:
            s00_ACBD = self.mll_ACBD
            s00_ADBC = self.mll_ADBC

        #TT_TT
        out[0*n:1*n, 0*n:1*n] = symcl(clAC,"TT")*symcl(clBD,"TT")*s00_ACBD/nu_l + \
                                symcl(clAD,"TT")*symcl(clBC,"TT")*s00_ADBC/nu_l
        
        if self.polar is False:
            return out
        
        #TT_EE
        out[0*n:1*n, 1*n:2*n] = symcl(clAC,"TE")*symcl(clBD,"TE")*s00_ACBD/nu_l + \
                                symcl(clAD,"TE")*symcl(clBC,"TE")*s00_ADBC/nu_l

        #TT_BB
        out[0*n:1*n, 2*n:3*n] = 0.

        #TT_TE
        out[0*n:1*n, 3*n:4*n] = symcl(clAC,"TT")*symcl(clBD,"TE")*s00_ACBD/nu_l + \
                                symcl(clAD,"TE")*symcl(clBC,"TT")*s00_ADBC/nu_l

        #TT_ET
        out[0*n:1*n, 4*n:5*n] = symcl(clAC,"TE")*symcl(clBD,"TT")*s00_ACBD/nu_l + \
                                symcl(clAD,"TT")*symcl(clBC,"TE")*s00_ADBC/nu_l

        #EE_TT
        out[1*n:2*n, 0*n:1*n] = symcl(clAC,"ET")*symcl(clBD,"ET")*s00_ACBD/nu_l + \
                                symcl(clAD,"ET")*symcl(clBC,"ET")*s00_ADBC/nu_l

        #EE_EE
        out[1*n:2*n, 1*n:2*n] = symcl(clAC,"EE")*symcl(clBD,"EE")*sPP_ACBD/nu_l + \
                                symcl(clAD,"EE")*symcl(clBC,"EE")*sPP_ADBC/nu_l

        #EE_BB
        out[1*n:2*n, 2*n:3*n] = ( symcl(clAC,"EE")*symcl(clBD,"EE") + \
                                  symcl(clAC,"EE")*symcl(clBD,"BB") + \
                                  symcl(clAC,"BB")*symcl(clBD,"EE") + \
                                  symcl(clAC,"BB")*symcl(clBD,"BB") )*sMM_ACBD/nu_l + \
                                ( symcl(clAD,"EE")*symcl(clBC,"EE") + \
                                  symcl(clAD,"EE")*symcl(clBC,"BB") + \
                                  symcl(clAD,"BB")*symcl(clBC,"EE") + \
                                  symcl(clAD,"BB")*symcl(clBC,"BB") )*sMM_ADBC/nu_l

        #EE_TE
        out[1*n:2*n, 3*n:4*n] = symcl(clAC,"ET")*symcl(clBD,"EE")*s0P_ACBD/nu_l + \
                                symcl(clAD,"EE")*symcl(clBC,"ET")*s0P_ACBD/nu_l

        #EE_ET
        out[1*n:2*n, 4*n:5*n] = symcl(clAC,"EE")*symcl(clBD,"ET")*s0P_ACBD/nu_l + \
                                symcl(clAD,"ET")*symcl(clBC,"EE")*s0P_ACBD/nu_l
        
        #BB_TT
        out[2*n:3*n, 0*n:1*n] = 0.

        #BB_EE
        out[2*n:3*n, 1*n:2*n] = ( symcl(clAC,"BB")*symcl(clBD,"BB") + \
                                  symcl(clAC,"BB")*symcl(clBD,"EE") + \
                                  symcl(clAC,"EE")*symcl(clBD,"BB") + \
                                  symcl(clAC,"EE")*symcl(clBD,"EE") )*sMM_ACBD/nu_l + \
                                ( symcl(clAD,"BB")*symcl(clBC,"BB") + \
                                  symcl(clAD,"BB")*symcl(clBC,"EE") + \
                                  symcl(clAD,"EE")*symcl(clBC,"BB") + \
                                  symcl(clAD,"EE")*symcl(clBC,"EE") )*sMM_ADBC/nu_l

        #BB_BB
        out[2*n:3*n, 2*n:3*n] = symcl(clAC,"BB")*symcl(clBD,"BB")*sPP_ACBD/nu_l + \
                                symcl(clAD,"BB")*symcl(clBC,"BB")*sPP_ADBC/nu_l

        #BB_TE
        out[2*n:3*n, 3*n:4*n] = 0.

        #BB_ET
        out[2*n:3*n, 4*n:5*n] = 0.

        #TE_TT
        out[3*n:4*n, 0*n:1*n] = symcl(clAC,"TT")*symcl(clBD,"ET")*s00_ACBD/nu_l + \
                                symcl(clAD,"TT")*symcl(clBC,"ET")*s00_ADBC/nu_l

        #TE_EE
        out[3*n:4*n, 1*n:2*n] = symcl(clAC,"TE")*symcl(clBD,"EE")*s0P_ACBD/nu_l + \
                                symcl(clAD,"TE")*symcl(clBC,"EE")*s0P_ADBC/nu_l

        #TE_BB
        out[3*n:4*n, 2*n:3*n] = 0.

        #TE_TE
        out[3*n:4*n, 3*n:4*n] = symcl(clAC,"TT")*symcl(clBD,"EE")*s0P_ACBD/nu_l + \
                                symcl(clAD,"TE")*symcl(clBC,"ET")*s00_ADBC/nu_l

        #TE_ET
        out[3*n:4*n, 4*n:5*n] = symcl(clAC,"TE")*symcl(clBD,"ET")*s00_ACBD/nu_l + \
                                symcl(clAD,"TT")*symcl(clBC,"EE")*s0P_ADBC/nu_l

        #ET_TT
        out[4*n:5*n, 0*n:1*n] = symcl(clAC,"ET")*symcl(clBD,"TT")*s00_ACBD/nu_l + \
                                symcl(clAD,"ET")*symcl(clBC,"TT")*s00_ADBC/nu_l

        #ET_EE
        out[4*n:5*n, 1*n:2*n] = symcl(clAC,"EE")*symcl(clBD,"TE")*s0P_ACBD/nu_l + \
                                symcl(clAD,"EE")*symcl(clBC,"TE")*s0P_ADBC/nu_l

        #ET_BB
        out[4*n:5*n, 2*n:3*n] = 0.

        #ET_TE
        out[4*n:5*n, 3*n:4*n] = symcl(clAC,"ET")*symcl(clBD,"TE")*s00_ACBD/nu_l + \
                                symcl(clAD,"EE")*symcl(clBC,"TT")*s0P_ADBC/nu_l

        #ET_ET
        out[4*n:5*n, 4*n:5*n] = symcl(clAC,"EE")*symcl(clBD,"TT")*s0P_ACBD/nu_l + \
                                symcl(clAD,"ET")*symcl(clBC,"TE")*s00_ADBC/nu_l
        
        return out

    def _block_to_mll( self, mll_blocks):
        if self.polar is False: return mll_blocks

        TT_TT, EE_EE, EE_BB, TE_TE, ET_ET = mll_blocks
        
        n = len(self.lbin)
        mll = np.zeros((5*n, 5*n))
        mll[0*n:1*n, 0*n:1*n] = TT_TT
        mll[1*n:2*n, 1*n:2*n] = EE_EE
        mll[2*n:3*n, 2*n:3*n] = EE_EE
        mll[1*n:2*n, 2*n:3*n] = EE_BB
        mll[2*n:3*n, 1*n:2*n] = EE_BB
        mll[3*n:4*n, 3*n:4*n] = TE_TE
        mll[4*n:5*n, 4*n:5*n] = ET_ET

        return mll
    
    def get_clcov_blocks(self, clAC, clBD, clAD, clBC, nsm=2):
        """
        Compute analytical covariance matrix for cross spectra: <AB,CD>
        tags=[TT,EE,BB,TE,ET]
        
        inputs:
            cl: 2d array (ntag,nbin)

        output:
            out: 2d array (5*nbin,5*nbin)
        """

        #use smooth data as signal model for covariance
        sclAC = self._smooth_cl( clAC, nsm=nsm)
        sclBD = self._smooth_cl( clBD, nsm=nsm)
        sclAD = self._smooth_cl( clAD, nsm=nsm)
        sclBC = self._smooth_cl( clBC, nsm=nsm)
        
        invmllAB = self._block_to_mll( self.invmll_AB)
        invmllCD = self._block_to_mll( self.invmll_CD)
        block = invmllAB @ self._get_pcl_cov(sclAC, sclBD, sclAD, sclBC) @ invmllCD.T
        
        return block



class Xpol_Wrapper(object):
    """
    (Cross-) power spectra estimation using the Xpol method.
    Hinshaw et al. 2003, Tristram et al. 2005.

    Wrapping to the C code.

    Example
    -------
    bins = Bins( lmins, lmaxs)
    xpol = Xpol(mask, bins)
    lbin = xpol.lbin
    biased, unbiased = xpol.get_spectra(map)
    biased, unbiased = xpol.get_spectra(map1, map2)

    """

    def __init__(self, mask, bins, mask2=None, polar=True, tmpdir=None, nprocs=4, verbose=False):
        """
        Parameters
        ----------
        mask : boolean Healpix map
            Mask defining the region of interest (of value True)
        bins: class binning (WARNING: for now only all multipoles)

        """
        
        if tmpdir is None:
            self._tmpdir = os.getenv("TMPDIR",".")
        else:
            self._tmpdir = tmpdir
        if not os.path.isdir(self._tmpdir):
            raise ValueError('No temporary directory.')
        
        self._runnb = np.random.randint(100000)
        
        self.mpirun = self._check_exe( "mpirun")+"/mpirun"
        self.bindir = self._check_exe( "xpol")
        self.lmin = int(bins.lmin)
        self.lmax = int(bins.lmax)
        self.nside = hp.npix2nside(len(mask))
        self.nprocs = nprocs
        
        self.nstokes = 3 if polar else 1
        
        self._verbose = verbose
        
        mask = np.asarray(mask)
        self._MLLFILE  = "{:s}/mll_{:d}".format(self._tmpdir,self._runnb)
        
        self._MASKFILE = []
        self._MASKFILE.append( "{:s}/mask_{:d}_0.fits".format(self._tmpdir,self._runnb))
        hp.write_map( self._MASKFILE[0], mask)
        if mask2 is not None:
            self._MASKFILE.append( "{:s}/mask_{:d}_1.fits".format(self._tmpdir,self._runnb))
            hp.write_map( self._MASKFILE[1], mask2)
        
        self._compute_mll()

        if not os.path.isfile( self._MLLFILE+"_0_0.fits"):
            raise ValueError('Mll not found.')
    
    def __del__(self):
        self._clean(   "mask_{:d}_0.fits".format(self._runnb))
        self._clean(   "mask_{:d}_1.fits".format(self._runnb))
        self._clean(    "mll_{:d}_*.fits".format(self._runnb))
        self._clean( "pseudo_{:d}_*.fits".format(self._runnb))
        self._clean(  "cross_{:d}_*.fits".format(self._runnb))

    def _clean(self, tmpfile):
        os.system( "rm -f {}/{}".format(self._tmpdir,tmpfile))

    def _check_exe( self, exe, path=None):
        bindir = None

        if path is None:
            paths = os.environ['PATH'].split(os.pathsep)
        else:
            paths = [path]

        for p in paths:
            if os.path.isfile( p+"/"+exe): bindir = p

        if bindir is None:
            raise ValueError( "Cannot find executables")
        
        return bindir

    def _compute_mll(self,verbose=True):
#        lmax = min( [2*self.lmax,3*self.nside-1])
        f = open( "{:s}/xpol_create_mll_{:d}.par".format(self._tmpdir,self._runnb), "w")
        f.write(      "nside = {}\n".format(self.nside    ))
        f.write(    "nstokes = {}\n".format(self.nstokes  ))
        f.write(       "lmax = {}\n".format(self.lmax     ))
        f.write(      "nmaps = {}\n".format(             2))
        f.write(   "weightI1 = {}\n".format(self._MASKFILE[0]))
        f.write(   "weightP1 = {}\n".format(self._MASKFILE[0]))
        if len(self._MASKFILE) == 2:
            f.write(   "weightI2 = {}\n".format(self._MASKFILE[1]))
            f.write(   "weightP2 = {}\n".format(self._MASKFILE[1]))
        f.write( "mlloutfile = {}\n".format(self._MLLFILE ))
        f.close()

        str_exe = "{} -n {:d} {}/xpol_create_mll {}/xpol_create_mll_{:d}.par".format(self.mpirun,self.nprocs,self.bindir,self._tmpdir,self._runnb)
        if not self._verbose:
            str_exe += " >& {}/xpol_create_mll_{:d}.out".format(self._tmpdir,self._runnb)
        err = os.system( str_exe)
        if err:
            os.system( "cat {}/xpol_create_mll_{:d}.out".format(self._tmpdir))
            raise ValueError( "Error create mll")
        self._clean( "xpol_create_mll_{:d}.par".format(self._runnb))
        self._clean( "xpol_create_mll_{:d}.out".format(self._runnb))


    def _compute_spectra( self, map1, map2, bell1, bell2):
        hp.write_map( "%s/map1_%d.fits" % (self._tmpdir,self._runnb), map1, overwrite=True)
        hp.write_map( "%s/map2_%d.fits" % (self._tmpdir,self._runnb), map2, overwrite=True)

        hp.write_cl( "%s/bell1_%d.fits"  % (self._tmpdir,self._runnb), bell1, overwrite=True)
        hp.write_cl( "%s/bell2_%d.fits"  % (self._tmpdir,self._runnb), bell2, overwrite=True)

        f = open( "%s/xpol_%d.par" % (self._tmpdir,self._runnb), "w")        
        f.write(   "nside = %d\n" % self.nside)
        f.write( "nstokes = %d\n" % self.nstokes)
        f.write(    "lmax = %d\n" %  self.lmax)
        f.write(   "nmaps = %d\n" %          2)        
        f.write( "mapfile1 = %s/map1_%s.fits\n" % (self._tmpdir,self._runnb))
        f.write( "mapfile2 = %s/map2_%s.fits\n" % (self._tmpdir,self._runnb))
        f.write( "weightI1 = %s\n" % self._MASKFILE[0])
        f.write( "weightP1 = %s\n" % self._MASKFILE[0])
        if len(self._MASKFILE) == 2:
            f.write(   "weightI2 = %s\n" % self._MASKFILE[1])
            f.write(   "weightP2 = %s\n" % self._MASKFILE[1])
    
        f.write( "mllinfile = %s\n" % self._MLLFILE)

        f.write( "bell1 = %s/bell1_%d.fits\n" % (self._tmpdir,self._runnb))
        f.write( "bell2 = %s/bell2_%d.fits\n" % (self._tmpdir,self._runnb))
    
        f.write(  "pseudo = %s/pseudo_%d\n"  % (self._tmpdir,self._runnb))    
        f.write(  "cross  = %s/cross_%d\n"  % (self._tmpdir,self._runnb))    
        f.write(  "no_error = 1\n")
    
        f.close()
        
        str_exe = "%s -n %d %s/xpol %s/xpol_%d.par" % (self.mpirun,self.nprocs,self.bindir,self._tmpdir,self._runnb)
        if not self._verbose:
            str_exe += " >& %s/xpol_%d.out" % (self._tmpdir,self._runnb)
        os.system( str_exe)
        
        #clean
        self._clean( "map1_%d.fits" % self._runnb)
        self._clean( "map2_%d.fits" % self._runnb)
        self._clean( "bell1_%d.fits" % self._runnb)
        self._clean( "bell2_%d.fits" % self._runnb)
        self._clean( "xpol_%d.par" % self._runnb)
        self._clean( "xpol_%d.out" % self._runnb)
    

    def get_spectra(self, map1, map2=None, bell1=None, bell2=None):

        #launch xpol
        if map2 is None: map2=map1
        if bell1 is None: bell1 = np.ones(self.lmax+1)
        if bell2 is None: bell2 = bell1
        self._compute_spectra( map1, map2, bell1, bell2)
        
        #set in one fits file
        pcl = np.zeros( (6, self.lmax+1))
        cltmp1 = hp.read_cl( "%s/pseudo_%d_0_1.fits"  % (self._tmpdir,self._runnb))
        cltmp2 = hp.read_cl( "%s/pseudo_%d_1_0.fits"  % (self._tmpdir,self._runnb))
        pcl = (cltmp1+cltmp2)/2.
        
        #set in one fits file
        cl  = np.zeros( (6, self.lmax+1))
        err = np.zeros( (6, self.lmax+1))
        for t in range(6):
            cltmp1 = fits.getdata( "%s/cross_%d_0_1.fits"  % (self._tmpdir,self._runnb), t+1)
            cltmp2 = fits.getdata( "%s/cross_%d_1_0.fits"  % (self._tmpdir,self._runnb), t+1)
            l = np.array(cltmp1.field(0),int)
            cl[t,l]  = (cltmp1.field(1)+cltmp2.field(1))/2./(l*(l+1)/2./np.pi)
            err[t,l] = np.sqrt((cltmp1.field(1)**2+cltmp2.field(1)**2)/2.)/(l*(l+1)/2./np.pi)
        
        #clean
        self._clean( "pseudo_%d_0_0.fits" % self._runnb)
        self._clean( "pseudo_%d_0_1.fits" % self._runnb)
        self._clean( "pseudo_%d_1_0.fits" % self._runnb)
        self._clean( "pseudo_%d_1_1.fits" % self._runnb)
        self._clean( "cross_%d_0_0.fits" % self._runnb)
        self._clean( "cross_%d_0_1.fits" % self._runnb)
        self._clean( "cross_%d_1_0.fits" % self._runnb)
        self._clean( "cross_%d_1_1.fits" % self._runnb)

        return pcl, cl, err



def fit_dipole(m, mask=None, bad=hp.UNSEEN):
    """Fit a dipole and a monopole to the map, excluding bad pixels.

    Parameters
    ----------
    m : float, array-like
      the map to which a dipole is fitted and subtracted, accepts masked maps
    m : float, array-like
      the mask with weight to be applied
    bad : float
      bad values of pixel, default to :const:`UNSEEN`.

    Returns
    -------
    res : tuple of length 2
      the monopole value in res[0] and the dipole vector (as array) in res[1]
    """
    m = np.asarray(m)
    npix = m.size
    nside = hp.npix2nside(npix)
    bunchsize = npix // 24 if nside > 128 else npix

    if mask is None:
        mask = np.ones( npix)        
        
    aa = np.zeros((4, 4), dtype=np.float64)
    v = np.zeros(4, dtype=np.float64)
    for ibunch in range(npix // bunchsize):
        ipix = np.arange(ibunch * bunchsize, (ibunch + 1) * bunchsize)
        ipix = ipix[(m.flat[ipix] != bad) & (np.isfinite(m.flat[ipix]))]
        x, y, z = hp.pix2vec(nside, ipix)
        aa[0, 0] += np.sum(mask[ipix])
        aa[1, 0] += np.sum(x*mask[ipix])
        aa[2, 0] += np.sum(y*mask[ipix])
        aa[3, 0] += np.sum(z*mask[ipix])
        aa[1, 1] += np.sum(mask.flat[ipix] * x * x)
        aa[2, 1] += np.sum(mask.flat[ipix] * x * y)
        aa[3, 1] += np.sum(mask.flat[ipix] * x * z)
        aa[2, 2] += np.sum(mask.flat[ipix] * y * y)
        aa[3, 2] += np.sum(mask.flat[ipix] * y * z)
        aa[3, 3] += np.sum(mask.flat[ipix] * z * z)
        v[0] += np.sum(mask.flat[ipix]*m.flat[ipix])
        v[1] += np.sum(mask.flat[ipix]*m.flat[ipix] * x)
        v[2] += np.sum(mask.flat[ipix]*m.flat[ipix] * y)
        v[3] += np.sum(mask.flat[ipix]*m.flat[ipix] * z)
    aa[0, 1] = aa[1, 0]
    aa[0, 2] = aa[2, 0]
    aa[0, 3] = aa[3, 0]
    aa[1, 2] = aa[2, 1]
    aa[1, 3] = aa[3, 1]
    aa[2, 3] = aa[3, 2]
    res = np.dot(np.linalg.inv(aa), v)
    mono = res[0]
    dipole = res[1:4]
    return mono, dipole

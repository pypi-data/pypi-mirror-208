def run_snid(filepath, lbda_range=[4000,9000], 
             delta_redshift=0.05, verbose=False,
             use_redshift=True, redshift=None,
             use_phase=True, phase=None, 
             **kwargs):

    spec_ = spectroscopy.Spectrum.from_filename(filepath)
    if lbda_range is not None:
        lbda_range[0] = np.max([lbda_range[0], int(spec_.lbda[10]+1)])
        lbda_range[1] = np.min([lbda_range[1], int(spec_.lbda[-10]-1)])

    if not use_phase and not use_redshift:
        return spec_.fit_snid(lbda_range=lbda_range,verbose=verbose, 
                             **kwargs)
    
    if redshift is None:
        t0, redshift = targets.loc[spec_.targetname][["t0","redshift"]].values
    else:
        t0 = targets.loc[spec_.targetname]["t0"]
        
    if phase is None and use_phase:
        phase = spec_.get_phase(t0, z=redshift)
        
    return spec_.fit_snid(lbda_range=lbda_range, 
                            phase=phase if use_phase else None, 
                            redshift=redshift if use_redshift else None, 
                            delta_redshift=delta_redshift, 
                            verbose=verbose, **kwargs)

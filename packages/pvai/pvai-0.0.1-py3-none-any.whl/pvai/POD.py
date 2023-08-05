class POD():
    '''
    obj_pod = POD() : creates object
    
    ---functions---
    obj_pod.fit(): gives temp_modes, sing_values, spatial_modes as attributes to obj_pod
    obj_pod.truncate(n): truncate the global library of modes and singular values (orginal library is retained)
    obj_pod.get_temp_modes(): outputs temporal modes for new samples, based on library of modes and singular values from fit
                              when using truncated = True, the truncated library is used
    obj_pod.reconstruct(): outputs reconstruction from temporal modes, based on library of modes and singular values from fit
                           when using truncated = True, the truncated library is used
    ---variables---
    obj_pod.mean_variables: the mean per variable of the original training data
    obj_pod.input_matrix: the centered training data ( original training data = centered + mean )
    obj_pod.temp_modes, obj_pod.sing_values, obj_pod.spatial_modes: original values corresponding to training data
    obj_pot.xxx_tr: the truncated version, allows to retain the original
    '''
    
    def __init__(self):
        print('new POD object')
        
    def fit(self,input_matrix):
        self.mean_variables = np.mean(input_matrix,axis=0)
        self.input_matrix = input_matrix - self.mean_variables
        self.temp_modes, self.sing_values, self.spatial_modes = np.linalg.svd(self.input_matrix, full_matrices=False)
        self.explained_variance_ratio_ = np.cumsum(self.sing_values ** 2) / np.sum(self.sing_values ** 2)
        print('fitted %i samples, for %i modes and %i variables'%(input_matrix.shape[0],len(self.sing_values),input_matrix.shape[1]))
        print(f'first mode where exp var ratio is larger than 99% is {np.where(self.explained_variance_ratio_>0.99)[0][0]}')
    def truncate(self,n):
        self.tm_tr = self.temp_modes[:,:n]
        self.sv_tr = self.sing_values[:n]
        self.sm_tr = self.spatial_modes[:n,:]
        print('truncated from %s to %s modes'%(str(self.spatial_modes.shape[0]),str(self.sm_tr.shape[0])))

    def get_temp_modes(self,input_samples,truncated=False):
        if truncated:
            temp_modes = (input_samples - self.mean_variables).dot(self.sm_tr.T).dot(np.linalg.inv(np.diag(self.sv_tr)))
        else:
            temp_modes = (input_samples - self.mean_variables).dot(self.spatial_modes.T).dot(np.linalg.inv(np.diag(self.sing_values)))         
        return(temp_modes)
    
    def reconstruct(self,temp_modes,truncated=False):
        if truncated:
            reconstruction = temp_modes.dot(np.diag(self.sv_tr)).dot(self.sm_tr)+self.mean_variables     
        else:
            reconstruction = temp_modes.dot(np.diag(self.sing_values)).dot(self.spatial_modes)+self.mean_variables
        return(reconstruction)
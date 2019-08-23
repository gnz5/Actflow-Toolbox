import numpy as np
import scipy.stats
from .model_compare_predicted_to_actual import *

def model_compare(target_actvect, model1_actvect, model2_actvect=None, full_report=False, print_report=True, print_by_condition=True, comparison_type='conditionwise_compthenavg', mean_absolute_error=False):
    """
    Function to compare prediction accuracies between models. If model2_actvect=None then the predictions are compared against a simple null model (e.g., r=0 for Pearson correlation). Note that this function cannot yet handle time series prediction testing.
    
    INPUTS
    target_actvect: node x condition x subject NumPy array, consisting of the to-be-predicted values the model predictions will be compared to. This should be a vector of activity values for each node (separately for each condition).
    
    model1_actvect: node x condition x subject NumPy array, consisting of Model 1's predicted values. This should be a vector of activity values for each node (separately for each condition).
    
    model2_actvect: Optional. A node x condition x subject NumPy array, consisting of Model 2's predicted values. This should be a vector of activity values for each node (separately for each condition).
    
    full_report: Calculate full report with all comparison types
    
    print_report: Print the model comparison report to screen
    
    print_by_condition: Print the model comparison report for each condition separately (only works if print_report is also True)
    
    comparison_type: The kind of comparison to calculate (when full_report=False). Options are:
    
        conditionwise_compthenavg - Compare-then-average condition-wise correlation between predicted and actual activations. This is run separately for each node, computing the correlation between the activations across conditions (which characterizes each node's response profile). The comparisons are computed separately for each subject, then results are summarized via averaging.
        conditionwise_avgthencomp - Average-then-compare condition-wise correlation between predicted and actual activations. This is run separately for each node, computing the correlation between the cross-condition activation patterns (which characterizes each node's response profile). Activations are averaged across subjects prior to comparison (sometimes called a "fixed effects" analysis), boosting signal-to-noise ratio but likely reducing dimensionality (through inter-subject averaging) and reducing the ability to assess the consistency of the result across subjects relative to compare-then-average.
        nodewise_compthenavg - Compare-then-average cross-node correlation between predicted and actual activations (whole-brain activation patterns). This is run separately for each condition, computing the correlation between the cross-node activation patterns (which characterizes each condition's response profile). The comparisons are computed separately for each subject, then results are summarized via averaging (sometimes called a "random effects" analysis).
        nodewise_avgthencomp - Average-then-compare cross-node correlation between predicted and actual activations (whole-brain activation patterns). This is run separately for each condition, computing the correlation between the cross-node activation patterns (which characterizes each condition's response profile). The comparisons are computed after averaging across subjects (sometimes called a "fixed effects" analysis).
        [TODO: subjwise_compthenavg (each node & condition based on individual differences)]
        
    mean_absolute_error: if True, compute the absolute mean error: mean(abs(a-p)), where a are the actual activations
    and p the predicted activations across all the nodes.
    
    
    OUTPUT
    output: a dictionary containing the following variables, depending on user input for full_report & reliability_type.
    
        When full_report=True: output contains variables for all reliability_type runs. 
        For model2_actvect is None, these variables are:
        conditionwise_compthenavg_output
        corr_conditionwise_compthenavg_bynode
        rankcorr_conditionwise_compthenavg_bynode
        conditionwise_avgthencomp_output
        corr_conditionwise_avgthencomp_bynode
        rankcorr_conditionwise_avgthencomp_bynode
        nodewise_compthenavg_output
        corr_nodewise_compthenavg_bycond
        nodewise_avgthencomp_output
        corr_nodewise_avgthencomp_bycond

        For when mean_absolute_error == True, these variables also include:
        maeAcc_bynode_compthenavg
        
        For when model2_actvect is not None, these variables also include:
        conditionwise_compthenavg_output_model2
        corr_conditionwise_compthenavg_bynode_model2
        rankcorr_conditionwise_compthenavg_bynode_model2
        conditionwise_avgthencomp_output_model2
        corr_conditionwise_avgthencomp_bynode_model2
        rankcorr_conditionwise_avgthencomp_bynode_model2
        nodewise_compthenavg_output_model2
        corr_nodewise_compthenavg_bycond_model2
        nodewise_avgthencomp_output_model2
        corr_nodewise_avgthencomp_bycond_model2
        
        For when mean_absolute_error == True and model2_actvect is not None, these variables also include:
        maeAcc_bynode_compthenavg_model2
    
    """
    
    nNodes=np.shape(target_actvect)[0]
    nConds=np.shape(target_actvect)[1]
    nSubjs=np.shape(target_actvect)[2]
    
    output = {}
    
    if print_report:
        print("===Comparing prediction accuracies between models (similarity between predicted and actual brain activation patterns)===")
    
    ### Condition-wise analyses (as opposed to node-wise)
        
    ## conditionwise_compthenavg - Compare-then-average condition-wise correlation between predicted and actual activations (only if more than one task condition)
    if full_report or comparison_type=='conditionwise_compthenavg':
        
        if nConds == 1:
            print("WARNING: Condition-wise calculations cannot be performed with only a single condition")
        else:

            #Test for accuracy of actflow prediction, separately for each subject ("compare-then-average")
            conditionwise_compthenavg_output = model_compare_predicted_to_actual(target_actvect, model1_actvect, comparison_type='conditionwise_compthenavg', mean_absolute_error=mean_absolute_error)
            corr_conditionwise_compthenavg_bynode = conditionwise_compthenavg_output['corr_conditionwise_compthenavg_bynode']
            rankcorr_conditionwise_compthenavg_bynode = conditionwise_compthenavg_output['rankcorr_conditionwise_compthenavg_bynode']
            
            #Add to output dictionary
            output.update({'conditionwise_compthenavg_output':conditionwise_compthenavg_output, 'corr_conditionwise_compthenavg_bynode':corr_conditionwise_compthenavg_bynode, 'rankcorr_conditionwise_compthenavg_bynode':rankcorr_conditionwise_compthenavg_bynode})

            
            if model2_actvect is None:
                ## Test against null model
                
                #Grand mean (across task) t-test
                [tval_ActflowPredAcc_nodemean,pval_ActflowPredAcc_nodemean] = scipy.stats.ttest_1samp(np.nanmean(np.ma.arctanh(corr_conditionwise_compthenavg_bynode),axis=0),0.0)
                #Set perfect rank correlations (rho=1) to be slightly lower (to avoid warnings) (rho=0.9999)
                rankcorr_conditionwise_compthenavg_bynode_mod=rankcorr_conditionwise_compthenavg_bynode.copy()
                rankcorr_conditionwise_compthenavg_bynode_mod=np.asarray(rankcorr_conditionwise_compthenavg_bynode_mod)
                rankcorr_conditionwise_compthenavg_bynode_mod[np.abs(rankcorr_conditionwise_compthenavg_bynode_mod)==1] = 0.9999
                [tval_ActflowPredAccRankCorr_nodemean,pval_ActflowPredAccRankCorr_nodemean] = scipy.stats.ttest_1samp(np.nanmean(np.ma.arctanh(rankcorr_conditionwise_compthenavg_bynode_mod),axis=0),0.0)
                
                
            else:
                ## Test model1 vs. model2 prediction accuracy
                
                # Test for accuracy of MODEL2 actflow prediction, separately for each subject ("compare-then-average")
                conditionwise_compthenavg_output_model2 = model_compare_predicted_to_actual(target_actvect, model2_actvect, comparison_type='conditionwise_compthenavg', mean_absolute_error=mean_absolute_error)
                corr_conditionwise_compthenavg_bynode_model2 = conditionwise_compthenavg_output_model2['corr_conditionwise_compthenavg_bynode']
                rankcorr_conditionwise_compthenavg_bynode_model2 = conditionwise_compthenavg_output_model2['rankcorr_conditionwise_compthenavg_bynode']
                
                #Grand mean (across task) t-test, model1 vs. model2 prediction accuracy
                model1_means=np.nanmean(np.ma.arctanh(corr_conditionwise_compthenavg_bynode),axis=0)
                model2_means=np.nanmean(np.ma.arctanh(corr_conditionwise_compthenavg_bynode_model2),axis=0)
                [tval_ActflowPredAcc_nodemean,pval_ActflowPredAcc_nodemean] = scipy.stats.ttest_1samp(np.subtract(model1_means,model2_means),0.0)
                #Set perfect rank correlations (rho=1) to be slightly lower (to avoid warnings) (rho=0.9999)
                rankcorr_conditionwise_compthenavg_bynode_model2_mod = rankcorr_conditionwise_compthenavg_bynode_model2.copy()
                rankcorr_conditionwise_compthenavg_bynode_model2_mod = np.asarray(rankcorr_conditionwise_compthenavg_bynode_model2_mod)
                rankcorr_conditionwise_compthenavg_bynode_model2_mod[np.abs(rankcorr_conditionwise_compthenavg_bynode_model2_mod) == 1] = 0.9999
                rankcorr_conditionwise_compthenavg_bynode_mod=rankcorr_conditionwise_compthenavg_bynode.copy()
                rankcorr_conditionwise_compthenavg_bynode_mod=np.asarray(rankcorr_conditionwise_compthenavg_bynode_mod)
                rankcorr_conditionwise_compthenavg_bynode_mod[np.abs(rankcorr_conditionwise_compthenavg_bynode_mod)==1] = 0.9999
                model1_rankcorr_means=np.nanmean(np.ma.arctanh(rankcorr_conditionwise_compthenavg_bynode_mod),axis=0)
                model2_rankcorr_means=np.nanmean(np.ma.arctanh(rankcorr_conditionwise_compthenavg_bynode_model2_mod),axis=0)
                [tval_ActflowPredAccRankCorr_nodemean,pval_ActflowPredAccRankCorr_nodemean] = scipy.stats.ttest_1samp(np.subtract(model1_rankcorr_means,model2_rankcorr_means),0.0)
                
                #Add to output dictionary
                output.update({'conditionwise_compthenavg_output_model2':conditionwise_compthenavg_output_model2, 'corr_conditionwise_compthenavg_bynode_model2':corr_conditionwise_compthenavg_bynode_model2, 'rankcorr_conditionwise_compthenavg_bynode_model2':rankcorr_conditionwise_compthenavg_bynode_model2})
                
            
            
            if print_report:
                print(" ")
                print("==Condition-wise correlations between predicted and actual activation patterns (calculated for each node separetely):==")
                print("--Compare-then-average (calculating prediction accuracies before cross-subject averaging):")
                print("Each correlation based on N conditions: " + str(nConds) + ", p-values based on N subjects (cross-subject variance in correlations): " + str(nSubjs))
                
                if model2_actvect is None:
                    print("Mean Pearson r=" + str("%.2f" % np.tanh(np.nanmean(np.nanmean(np.ma.arctanh(corr_conditionwise_compthenavg_bynode))))) + ", t-value vs. 0: " + str("%.2f" % tval_ActflowPredAcc_nodemean) + ", p-value vs. 0: " + str(pval_ActflowPredAcc_nodemean))
                    print("Mean rank-correlation rho=" + str("%.2f" % np.nanmean(np.nanmean(rankcorr_conditionwise_compthenavg_bynode))) + ", t-value vs. 0: " + str("%.2f" % tval_ActflowPredAccRankCorr_nodemean) + ", p-value vs. 0: " + str(pval_ActflowPredAccRankCorr_nodemean))
                    
                else:
                    meanRModel1=np.tanh(np.nanmean(np.nanmean(np.ma.arctanh(corr_conditionwise_compthenavg_bynode))))
                    print("Model1 mean Pearson r=" + str("%.2f" % meanRModel1))
                    meanRModel2=np.tanh(np.nanmean(np.nanmean(np.ma.arctanh(corr_conditionwise_compthenavg_bynode_model2))))
                    print("Model2 mean Pearson r=" + str("%.2f" % meanRModel2))
                    meanRModelDiff=meanRModel1-meanRModel2
                    print("R-value difference = " + str("%.2f" % meanRModelDiff))
                    print("Model1 vs. Model2 T-value: " + str("%.2f" % tval_ActflowPredAcc_nodemean) + ", p-value: " + str(pval_ActflowPredAcc_nodemean))
                    
                    meanRhoModel1=np.tanh(np.nanmean(np.nanmean(np.ma.arctanh(rankcorr_conditionwise_compthenavg_bynode))))
                    print("Model1 mean rank-correlation rho=" + str("%.2f" % meanRhoModel1))
                    meanRhoModel2=np.tanh(np.nanmean(np.nanmean(np.ma.arctanh(rankcorr_conditionwise_compthenavg_bynode_model2))))
                    print("Model2 mean rank-correlation rho=" + str("%.2f" % meanRhoModel2))
                    meanRhoModelDiff=meanRhoModel1-meanRhoModel2
                    print("Rho-value difference = " + str("%.2f" % meanRModelDiff))
                    print("Model1 vs. Model2 T-value: " + str("%.2f" % tval_ActflowPredAccRankCorr_nodemean) + ", p-value: " + str(pval_ActflowPredAccRankCorr_nodemean))
                    
              
            if mean_absolute_error:
            
                maeAcc_bynode_compthenavg = conditionwise_compthenavg_output['maeAcc_bynode_compthenavg']
                
                #Add to output dictionary
                output.update({'maeAcc_bynode_compthenavg':maeAcc_bynode_compthenavg})
                
                if model2_actvect is not None:
                    maeAcc_bynode_compthenavg_model2 = conditionwise_compthenavg_output_model2['maeAcc_bynode_compthenavg']
                    
                    #Add to output dictionary
                    output.update({'maeAcc_bynode_compthenavg_model2':maeAcc_bynode_compthenavg_model2})
            
                if print_report:
                    print(" ")
                    print("==Condition-wise Mean Absolute Error (MAE) between predicted and actual activation patterns (calculated for each node separateley):==")

                    print("--Compare-then-average (calculating MAE accuracies before cross-subject averaging):")
                    print("Each MAE based on N conditions: " + str(nConds))
                    
                    if model2_actvect is None:
                        print("Mean MAE =" + str("%.2f" % np.nanmean(np.nanmean(maeAcc_bynode_compthenavg))))
                    else:
                        print("Model1 mean MAE = " + str("%.2f" % np.nanmean(np.nanmean(maeAcc_bynode_compthenavg))))
                        print("Model2 mean MAE = " + str("%.2f" % np.nanmean(np.nanmean(maeAcc_bynode_compthenavg_model2))))
                        print("Model1 vs. Model2 mean MAE difference = " + str("%.2f" % np.subtract(np.nanmean(np.nanmean(maeAcc_bynode_compthenavg)), np.nanmean(np.nanmean(maeAcc_bynode_compthenavg_model2)))))
                        

    
    
    ## conditionwise_avgthencomp - Average-then-compare condition-wise correlation between predicted and actual activations (only if more than one task condition)
    if full_report or comparison_type=='conditionwise_avgthencomp':
        
        if nConds == 1:
            print("WARNING: Condition-wise calculations cannot be performed with only a single condition")
        else:
    
            #Test for accuracy of actflow prediction, separately for each subject ("average-then-compare")
            conditionwise_avgthencomp_output = model_compare_predicted_to_actual(target_actvect, model1_actvect, comparison_type='conditionwise_avgthencomp', mean_absolute_error=mean_absolute_error)
            corr_conditionwise_avgthencomp_bynode = conditionwise_avgthencomp_output['corr_conditionwise_avgthencomp_bynode']
            rankcorr_conditionwise_avgthencomp_bynode = conditionwise_avgthencomp_output['rankcorr_conditionwise_avgthencomp_bynode']
            
            #Add to output dictionary
            output.update({'conditionwise_avgthencomp_output':conditionwise_avgthencomp_output, 'corr_conditionwise_avgthencomp_bynode':corr_conditionwise_avgthencomp_bynode, 'rankcorr_conditionwise_avgthencomp_bynode':rankcorr_conditionwise_avgthencomp_bynode})
            
            if model2_actvect is not None:
                # Test for accuracy of MODEL2 actflow prediction, after averaging across subjects ("average-then-compare")
                conditionwise_avgthencomp_output_model2 = model_compare_predicted_to_actual(target_actvect, model2_actvect, comparison_type='conditionwise_avgthencomp', mean_absolute_error=mean_absolute_error)
                corr_conditionwise_avgthencomp_bynode_model2 = conditionwise_avgthencomp_output_model2['corr_conditionwise_avgthencomp_bynode']
                rankcorr_conditionwise_avgthencomp_bynode_model2 = conditionwise_avgthencomp_output_model2['rankcorr_conditionwise_avgthencomp_bynode']
                
                #Add to output dictionary
                output.update({'conditionwise_avgthencomp_output_model2':conditionwise_avgthencomp_output_model2, 'corr_conditionwise_avgthencomp_bynode_model2':corr_conditionwise_avgthencomp_bynode_model2, 'rankcorr_conditionwise_avgthencomp_bynode_model2':rankcorr_conditionwise_avgthencomp_bynode_model2})

            if print_report:
                print(" ")
                print("==Condition-wise correlations between predicted and actual activation patterns (calculated for each node separetely):==")
                print("--Average-then-compare (calculating prediction accuracies after cross-subject averaging):")
                print("Each correlation based on N conditions: " + str(nConds))
                
                if model2_actvect is None:
                    print("Mean Pearson r=" + str("%.2f" % np.tanh(np.nanmean(np.ma.arctanh(corr_conditionwise_avgthencomp_bynode)))))
                    print("Mean rank-correlation rho=" + str("%.2f" % np.nanmean(rankcorr_conditionwise_avgthencomp_bynode)))
                else:
                    meanRModel1=np.tanh(np.nanmean(np.nanmean(np.ma.arctanh(corr_conditionwise_avgthencomp_bynode))))
                    print("Model1 Mean Pearson r=" + str("%.2f" % meanRModel1))
                    meanRModel2=np.tanh(np.nanmean(np.nanmean(np.ma.arctanh(corr_conditionwise_avgthencomp_bynode_model2))))
                    print("Model2 Mean Pearson r=" + str("%.2f" % meanRModel2))
                    meanRModelDiff=meanRModel1-meanRModel2
                    print("R-value difference = " + str("%.2f" % meanRModelDiff))

            if mean_absolute_error:
            
                maeAcc_bynode_avgthencomp = conditionwise_avgthencomp_output['maeAcc_bynode_avgthencomp']
                
                #Add to output dictionary
                output.update({'maeAcc_bynode_avgthencomp':maeAcc_bynode_avgthencomp})
            
                if print_report:
                    print(" ")
                    print("==Condition-wise Mean Absolute Error (MAE) between predicted and actual activation patterns (calculated for each node separateley):==")

                    print("--Average-then-compare (calculating MAE accuracies after cross-subject averaging):")
                    print("Each MAE based on N conditions: " + str(nConds))
                    print("Mean MAE=" + str("%.2f" % np.nanmean(maeAcc_bynode_avgthencomp)))
        
    
    
    ### Node-wise analyses (as opposed to condition-wise)

    ## nodewise_compthenavg - Compare-then-average cross-node correlation between predicted and actual activations (whole-brain activation patterns)
    if full_report or comparison_type=='nodewise_compthenavg':
        
        #Test for accuracy of actflow prediction, separately for each subject ("compare-then-average")
        nodewise_compthenavg_output = model_compare_predicted_to_actual(target_actvect, model1_actvect, comparison_type='nodewise_compthenavg', mean_absolute_error=mean_absolute_error)
        corr_nodewise_compthenavg_bycond = nodewise_compthenavg_output['corr_nodewise_compthenavg_bycond']
        
        #Add to output dictionary
        output.update({'nodewise_compthenavg_output':nodewise_compthenavg_output, 'corr_nodewise_compthenavg_bycond':corr_nodewise_compthenavg_bycond})
        
        if model2_actvect is None:
            ## Test against null model
            
            #Run t-tests to quantify cross-subject consistency, by condition, Pearson correlations
            tval_ActflowPredAccCorr_bycond=np.zeros(nConds)
            pval_ActflowPredAccCorr_bycond=np.zeros(nConds)
            for condNum in range(nConds):
                [tval_ActflowPredAccCorr_bycond[condNum],pval_ActflowPredAccCorr_bycond[condNum]] = scipy.stats.ttest_1samp(np.ma.arctanh(corr_nodewise_compthenavg_bycond[condNum]),0.0)
                
            #Grand mean (across task) t-test
            [tval_ActflowPredAcc_condmean,pval_ActflowPredAcc_condmean] = scipy.stats.ttest_1samp(np.nanmean(np.ma.arctanh(corr_nodewise_compthenavg_bycond),axis=0),0.0)
            
        else:
            ## Test model1 vs. model2 prediction accuracy

            # Test for accuracy of MODEL2 actflow prediction, separately for each subject ("compare-then-average")
            nodewise_compthenavg_output_model2 = model_compare_predicted_to_actual(target_actvect, model2_actvect, comparison_type='nodewise_compthenavg', mean_absolute_error=mean_absolute_error)
            corr_nodewise_compthenavg_bycond_model2 = nodewise_compthenavg_output_model2['corr_nodewise_compthenavg_bycond']
            
            #Add to output dictionary
            output.update({'nodewise_compthenavg_output_model2':nodewise_compthenavg_output_model2, 'corr_nodewise_compthenavg_bycond_model2':corr_nodewise_compthenavg_bycond_model2})
            
            #Run t-tests to quantify cross-subject consistency, by condition, Pearson correlations
            tval_ActflowPredAccCorr_Model1Vs2_bycond=np.zeros(nConds)
            pval_ActflowPredAccCorr_Model1Vs2_bycond=np.zeros(nConds)
            for condNum in range(nConds):
                model1Vals=np.ma.arctanh(corr_nodewise_compthenavg_bycond[condNum])
                model2Vals=np.ma.arctanh(corr_nodewise_compthenavg_bycond_model2[condNum])
                [tval_ActflowPredAccCorr_Model1Vs2_bycond[condNum],pval_ActflowPredAccCorr_Model1Vs2_bycond[condNum]] = scipy.stats.ttest_1samp(np.subtract(model1Vals,model2Vals),0.0)

            #Grand mean (across nodes) t-test, model1 vs. model2 prediction accuracy
            model1_means=np.nanmean(np.ma.arctanh(corr_nodewise_compthenavg_bycond),axis=0)
            model2_means=np.nanmean(np.ma.arctanh(corr_nodewise_compthenavg_bycond_model2),axis=0)
            [tval_ActflowPredAcc_condmean,pval_ActflowPredAcc_condmean] = scipy.stats.ttest_1samp(np.subtract(model1_means,model2_means),0.0)
        
        if print_report:
            print(" ")
            print("==Node-wise (spatial) correlations between predicted and actual activation patterns (calculated for each condition separetely):==")
            print("--Compare-then-average (calculating prediction accuracies before cross-subject averaging):")
            print("Each correlation based on N nodes: " + str(nNodes) + ", p-values based on N subjects (cross-subject variance in correlations): " + str(nSubjs))
                
            if model2_actvect is None:
                    
                print("Cross-condition mean r=" + str("%.2f" % np.tanh(np.nanmean(np.nanmean(np.ma.arctanh(corr_nodewise_compthenavg_bycond))))) + ", t-value vs. 0: " + str("%.2f" % tval_ActflowPredAcc_condmean) + ", p-value vs. 0: " + str(pval_ActflowPredAcc_condmean))
                
                if print_by_condition:
                     print("By task condition:")
                     for condNum in range(nConds):
                         print("Condition " + str(condNum+1) + ": r=" + str("%.2f" % np.tanh(np.nanmean(np.ma.arctanh(corr_nodewise_compthenavg_bycond[condNum])))) + ", t-value vs. 0: " + str("%.2f" % tval_ActflowPredAccCorr_bycond[condNum]) + ", p-value vs. 0: " + str(pval_ActflowPredAccCorr_bycond[condNum]))
                            
            else:
                
                meanRModel1=np.tanh(np.nanmean(np.nanmean(np.ma.arctanh(corr_nodewise_compthenavg_bycond))))
                print("Model1 mean Pearson r=" + str("%.2f" % meanRModel1))
                meanRModel2=np.tanh(np.nanmean(np.nanmean(np.ma.arctanh(corr_nodewise_compthenavg_bycond_model2))))
                print("Model2 mean Pearson r=" + str("%.2f" % meanRModel2))
                meanRModelDiff=meanRModel1-meanRModel2
                print("R-value difference = " + str("%.2f" % meanRModelDiff))
                print("Model1 vs. Model2 T-value: " + str("%.2f" % tval_ActflowPredAcc_condmean) + ", p-value: " + str(pval_ActflowPredAcc_condmean))
                
                if print_by_condition:
                    print("By task condition:")
                    for condNum in range(nConds):
                        model1R=np.tanh(np.nanmean(np.ma.arctanh(corr_nodewise_compthenavg_bycond[condNum])))
                        model2R=np.tanh(np.nanmean(np.ma.arctanh(corr_nodewise_compthenavg_bycond_model2[condNum])))
                        print("Condition " + str(condNum+1) + ": Model 1 r=" + str("%.2f" % model1R) + ", Model 2 r=" + str("%.2f" % model2R) + ", Model 1 vs. 2 R-value difference =" + str("%.2f" % np.subtract(model1R, model2R)) + ", t-value Model1 vs. Model2: " + str("%.2f" % tval_ActflowPredAccCorr_Model1Vs2_bycond[condNum]) + ", p-value vs. 0: " + str(pval_ActflowPredAccCorr_Model1Vs2_bycond[condNum]))

                        
                
    ## nodewise_avgthencomp - Average-then-compare cross-node correlation between predicted and actual activations (whole-brain activation patterns)

    if full_report or comparison_type=='nodewise_avgthencomp':
        
        #Test for accuracy of actflow predictions, after averaging across subjects ("average-then-compare")
        nodewise_avgthencomp_output = model_compare_predicted_to_actual(target_actvect, model1_actvect, comparison_type='nodewise_avgthencomp', mean_absolute_error=mean_absolute_error)
        corr_nodewise_avgthencomp_bycond = nodewise_avgthencomp_output['corr_nodewise_avgthencomp_bycond']
        
        #Add to output dictionary
        output.update({'nodewise_avgthencomp_output':nodewise_avgthencomp_output, 'corr_nodewise_avgthencomp_bycond':corr_nodewise_avgthencomp_bycond})
        
        if model2_actvect is not None:
            #Test for accuracy of actflow predictions, after averaging across subjects ("average-then-compare")
            nodewise_avgthencomp_output_model2 = model_compare_predicted_to_actual(target_actvect, model2_actvect, comparison_type='nodewise_avgthencomp', mean_absolute_error=mean_absolute_error)
            corr_nodewise_avgthencomp_bycond_model2 = nodewise_avgthencomp_output_model2['corr_nodewise_avgthencomp_bycond']
                
            #Add to output dictionary
            output.update({'nodewise_avgthencomp_output_model2':nodewise_avgthencomp_output_model2, 'corr_nodewise_avgthencomp_bycond_model2':corr_nodewise_avgthencomp_bycond_model2})
            
        
        if print_report:
            print(" ")
            print("==Node-wise (spatial) correlations between predicted and actual activation patterns (calculated for each condition separetely):==")
            print("--Average-then-compare (calculating prediction accuracies after cross-subject averaging):")
            print("Each correlation based on N nodes: " + str(nNodes) + ", p-values based on N subjects (cross-subject variance in correlations): " + str(nSubjs))
                
            if model2_actvect is None:
    
                print("Mean r=" + str("%.2f" % np.tanh(np.nanmean(np.ma.arctanh(corr_nodewise_avgthencomp_bycond)))))
        
                if print_by_condition:
                    print("By task condition:")
                    for condNum in range(nConds):
                        print("Condition " + str(condNum+1) + ": r=" + str("%.2f" % corr_nodewise_avgthencomp_bycond[condNum]))
                        
            else:
                
                model1MeanR=np.tanh(np.nanmean(np.ma.arctanh(corr_nodewise_avgthencomp_bycond)))
                model2MeanR=np.tanh(np.nanmean(np.ma.arctanh(corr_nodewise_avgthencomp_bycond_model2)))
                print("Mean Model1 r=" + str("%.2f" % model1MeanR))
                print("Mean Model2 r=" + str("%.2f" % model2MeanR))
                print("Mean Model1 vs. Model2 R-value difference=" + str("%.2f" % (model1MeanR - model2MeanR)))
                
                if print_by_condition:
                    print("By task condition:")
                    for condNum in range(nConds):
                        print("Condition " + str(condNum+1) + ": Model1 r=" + str("%.2f" % corr_nodewise_avgthencomp_bycond[condNum]) + ", Model2 r=" + str("%.2f" % corr_nodewise_avgthencomp_bycond_model2[condNum]) + ", Model 1 vs. Model2 R-value difference=" + str("%.2f" % np.subtract(corr_nodewise_avgthencomp_bycond[condNum], corr_nodewise_avgthencomp_bycond_model2[condNum])))
                        
    return output              
                
                

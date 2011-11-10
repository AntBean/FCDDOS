"""
output file name format
numattacker_trainingset.testingset.arff
where training set may composed of 1 or more set distibguised by '_'
similarly testing set may composed of 1 or more set distibguised by '_'
for ex:
    100_userdataset_agg_mild.agg_stealth.arff
"""
import string
import datetime
import time
import pyparsing
import argparse
import os, sys
import re
import random
import datetime
import time
from argparse import ArgumentParser, ArgumentTypeError

# parse commandline arguments
def parseCmdArgs():
    desc = "take output from parseApacheLog & generate arff file"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-u", "--user-parsed-file",
            help="File container parsed user traffic")
    parser.add_argument("-o", "--output-dir",
            help="output directory of all files")
    parser.add_argument("-f", "--arff-format-file",
            help="arff format file")
    args = parser.parse_args()
    return args

#parseapache related command
args = parseCmdArgs()
MAX_ATT_LEVEL = 9

#later we will have more test cases when fully automated
#currently we will generate test only for level 9 aggressive, level 9 mild
#level 9 stealth
#number of attacker
n = [100,500,1000]
#range of pause between session
p = ["31-40","41-600","601-700"]
#range of number of request in  a session
r = ["51-88","31-50","21-30"]
#range of gap between two request in  a session
a = ["11-20","21-40","41-88"]
# outfilename
att_type = ["agg","mild","stealth"]
attack_generate_start_cmd = "python attack_generate.py"

att_level = MAX_ATT_LEVEL
att_id = 1
nj = 0
pk = 0
rl =0;
am = 0;

output_dir = args.output_dir
user_parsed_file = args.user_parsed_file
arff_format_file = args.arff_format_file
weka_train_test_list = []
parse_apache_start_command = "python parseApacheLog.py"

#generate_experiment command
generate_experiment_start_command = "python generate_experiment.py"

#python parseApacheLog.py -i symposium_data/scenario2 -o symposium_data/scenario2_parsed
exprnum =1
#parse commandlist arguments    
for num in n:
    attacker_list = []
    for index in range(len(p)):
        pause = p[index]
        attacker = att_type[index]
        rate = r[index]
        gap = p[index]
        #print num,pause,rate,gap,attacker
                
        #prepare & write attack generate command
        attack_generate_full_command = attack_generate_start_cmd + \
                            " -n "+str(num)+\
                            " -p "+pause+\
                            " -r "+rate+\
                            " -a "+gap

        attack_generate_ofile = output_dir
        #attack_generate_ofile= attack_generate_ofile+"attacker" 
        #attack_generate_ofile = "".join([str(attack_generate_ofile),str(att_id)])
        #attack_generate_ofile = "_".join([str(attack_generate_ofile),str(attacker)])
        attack_generate_ofile = "".join([str(attack_generate_ofile),str(attacker)])
        attack_generate_full_command = attack_generate_full_command+\
                                                " -o "+attack_generate_ofile
        att_id+=1
        #start of test message
        #print 'echo "<-----------------TestStarted-------------------------->"'
        #print 'echo "'+attack_generate_full_command+str('"')
        print attack_generate_full_command

        #prepare & write parsepache command
        parsed_apache_ofile = attack_generate_ofile + "_" + "parsed"
        parse_apache_full_command = parse_apache_start_command + \
                    " -i "+attack_generate_ofile+\
                    " -o "+parsed_apache_ofile
        print parse_apache_full_command
        #add to the list so later we can generate combination of 
        #train & testing set
        attacker_list.append(parsed_apache_ofile)
        #prepare & write the command the to convert just the attacker
        #file for testing
        #print 'echo "<-----------------TestEnds-------------------------->"'
    

    #total 13 different scenario for 1 value of n
    
    #6 training sets with size 1
    
    for i in range(len(attacker_list)):
        j =i
        while j < len(attacker_list):
            training_set = user_parsed_file+" "+attacker_list[i]
            testing_set = attacker_list[j]
            #prepare & write mixattack traffic & user traffic
            training_ofile = output_dir+"Expr"+str(exprnum)+"_"+"Train"+"_"+str(num)+"."+\
                                str(os.path.basename(attacker_list[i]))+\
                                ".arff"
            testing_ofile = output_dir+"Expr"+str(exprnum)+"_"+"Test"+"_"+str(num)+"."+\
                                str(os.path.basename(attacker_list[j]))+\
                                ".arff"
            training_ofile=training_ofile.replace("_parsed","")
            testing_ofile=testing_ofile.replace("_parsed","")
            generate_experiment_full_command = generate_experiment_start_command + \
                                              " -t "+training_set + \
                                              " -v "+testing_set + \
                                              " -f "+arff_format_file + \
                                              " -vo "+testing_ofile + \
                                              " -to "+training_ofile
            print generate_experiment_full_command
            weka_train_test_list.append([training_ofile,testing_ofile]) 
            exprnum +=1
            j+=1

    # 6 training set with size 2, 3 testing set of size 2
    # 3 testing set of 1
    for i in range(len(attacker_list)-1):
        j = i+1
        while j < len(attacker_list):
            tempset = set([k for k in range(len(attacker_list))])
            training_set = user_parsed_file+" "+attacker_list[i]+" "+attacker_list[j]
            #test set of size 2
            testing_set = attacker_list[i]+" "+attacker_list[j]
            #prepare & write mixattack traffic & user traffic
            training_ofile = output_dir+"Expr"+str(exprnum)+"_"+"Train"+"_"+str(num)+"."+\
                                str(os.path.basename(attacker_list[i]))+\
                                "_"+\
                                str(os.path.basename(attacker_list[j]))+\
                                ".arff"
            testing_ofile = output_dir+"Expr"+str(exprnum)+"_"+"Test"+"_"+str(num)+"."+\
                                str(os.path.basename(attacker_list[i]))+\
                                "_"+\
                                str(os.path.basename(attacker_list[j]))+\
                                ".arff"
            training_ofile=training_ofile.replace("_parsed","")
            testing_ofile=testing_ofile.replace("_parsed","")
            generate_experiment_full_command = generate_experiment_start_command + \
                                              " -t "+training_set + \
                                              " -v "+testing_set + \
                                              " -f "+arff_format_file + \
                                              " -vo "+testing_ofile + \
                                              " -to "+training_ofile
            print generate_experiment_full_command
            weka_train_test_list.append([training_ofile,testing_ofile]) 
            
            exprnum +=1
            
            #test set of size1
            tempset.remove(i)
            tempset.remove(j)
            testing_set = attacker_list[tempset.pop()]
            #prepare & write mixattack traffic & user traffic
            training_ofile = output_dir+"Expr"+str(exprnum)+"_"+"Train"+"_"+str(num)+"."+\
                                str(os.path.basename(attacker_list[i]))+\
                                "_"+\
                                str(os.path.basename(attacker_list[j]))+\
                                ".arff"
            testing_ofile = output_dir+"Expr"+str(exprnum)+"_"+"Test"+"_"+str(num)+"."+\
                                str(os.path.basename(testing_set))+\
                                ".arff"
            training_ofile=training_ofile.replace("_parsed","")
            testing_ofile=testing_ofile.replace("_parsed","")
            generate_experiment_full_command = generate_experiment_start_command + \
                                              " -t "+training_set + \
                                              " -v "+testing_set + \
                                              " -f "+arff_format_file + \
                                              " -vo "+testing_ofile + \
                                              " -to "+training_ofile
            print generate_experiment_full_command
            weka_train_test_list.append([training_ofile,testing_ofile]) 
            exprnum +=1
            
            j+=1

    #training set of size 3 & testing 1
    training_set = user_parsed_file+" "+attacker_list[0]+" "+attacker_list[1]+\
                                        " "+attacker_list[2]
    testing_set = attacker_list[0]
    #prepare & write mixattack traffic & user traffic
    training_ofile = output_dir+"Expr"+str(exprnum)+"_"+"Train"+"_"+str(num)+"."+\
                        str(os.path.basename(attacker_list[0]))+\
                        "_"+\
                        str(os.path.basename(attacker_list[1]))+\
                        "_"+\
                        str(os.path.basename(attacker_list[2]))+\
                        ".arff"
    testing_ofile = output_dir+"Expr"+str(exprnum)+"_"+"Test"+"_"+str(num)+"."+\
                        str(os.path.basename(attacker_list[0]))+\
                        ".arff"
    training_ofile=training_ofile.replace("_parsed","")
    testing_ofile=testing_ofile.replace("_parsed","")
    generate_experiment_full_command = generate_experiment_start_command + \
                                    " -t "+training_set + \
                                    " -v "+testing_set + \
                                    " -f "+arff_format_file + \
                                    " -vo "+testing_ofile + \
                                    " -to "+training_ofile
    print generate_experiment_full_command
    weka_train_test_list.append([training_ofile,testing_ofile]) 
    exprnum +=1
    
#now run experiments using weka
#just print the accuracy information for training & testing
weka_start_command = "java weka.classifiers.trees.J48"
 
for tr_ofile,ts_ofile in weka_train_test_list:
    print 'echo "<-----------------Experiment Started-------------------------->"'
    print 'echo "Training Set = '+ tr_ofile +'"'
    print 'echo "Testing Set = '+ ts_ofile +'"'
    weka_full_command = weka_start_command + \
                            " -t "+tr_ofile+\
                            " -T "+ts_ofile+\
                            " -o "
    print weka_full_command
    print 'echo "<-----------------Experiment Ends----------------------------->"'
    
#will be used for large number of test cases
"""
for num in n:
    print num,
    for pause,attacker in [(pause,attacker) for pause in p for attacker in att_type]:
        print pause,
        att_level = MAX_ATT_LEVEL
        for rate in r:
            print rate,
            for gap in a:
                print gap
                
                #prepare & write attack generate command
                attack_generate_full_command = attack_generate_start_cmd + \
                                            " -n "+str(num)+\
                                            " -p "+pause+\
                                            " -r "+rate+\
                                            " -a "+gap

                attack_generate_ofile = output_dir
                attack_generate_ofile= attack_generate_ofile+"attacker" 
                attack_generate_ofile = "".join([str(attack_generate_ofile),str(att_id)])
                attack_generate_ofile = "_".join([str(attack_generate_ofile),str(attacker)])
                attack_generate_ofile = "_".join([str(attack_generate_ofile),str(att_level)])
                attack_generate_full_command = attack_generate_full_command+\
                                                " -o "+attack_generate_ofile
                att_id+=1
                att_level-= 1
                #start of test message
                #print 'echo "<-----------------TestStarted-------------------------->"'
                #print 'echo "'+attack_generate_full_command+str('"')
                #print attack_generate_full_command

                #prepare & write parsepache command
                parsed_apache_ofile = attack_generate_ofile + "_" + "parsed"
                parse_apache_full_command = parse_apache_start_command + \
                                            " -i "+attack_generate_ofile+\
                                            " -o "+parsed_apache_ofile
                #print parse_apache_full_command
                #mixing part should be done separately
                #prepare & write mixattack traffic & user traffic
                training_ofile = parsed_apache_ofile + ".arff"
                generate_experiment_full_command = generate_experiment_start_command + \
                                          " -u "+user_parsed_file + \
                                          " -a "+parsed_apache_ofile + \
                                          " -f "+arff_format_file + \
                                          " -o "+training_ofile
                print generate_experiment_full_command
                
                prepare & write the command the to convert just the attacker
                file for testing
                print 'echo "<-----------------TestEnds-------------------------->"'
            
"""

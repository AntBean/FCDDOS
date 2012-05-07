export CLASSPATH=/home/natty/weka/weka.jar:$CLASSPATH


:<<1supercalifragilisticexpialidocious
time python runAggressiveAttackerExperiment.py -u /media/storage/Experiments/DataSets/filtered/ISI_300KReq/ISI1 /media/storage/Experiments/DataSets/filtered/ISI_300KReq/ISI2 /media/storage/Experiments/DataSets/filtered/ISI_300KReq/ISI3 -o /media/storage/Experiments/DynamicModel/RF/ISI_300KReq/ -r 100 -t 100


time python runAggressiveAttackerExperiment.py -u /media/storage/Experiments/DataSets/filtered/ISI_500KReq/ISI1 /media/storage/Experiments/DataSets/filtered/ISI_500KReq/ISI2 -o /media/storage/Experiments/DynamicModel/RF/ISI_500KReq/ -r 100 -t 100

time python runReqestSemanticModelExperiments.py -p /media/storage/Experiments/DynamicModel/RF/ISI_300KReq/ISI1_u /media/storage/Experiments/DynamicModel/RF/ISI_300KReq/ISI2_u /media/storage/Experiments/DynamicModel/RF/ISI_300KReq/ISI3_u -o /media/storage/Experiments/SemanticModel/RF/ISI_300KReq/

time python runReqestSemanticModelExperiments.py -p /media/storage/Experiments/DynamicModel/RF/ISI_500KReq/ISI1_u -o /media/storage/Experiments/SemanticModel/RF/ISI_500KReq/

1supercalifragilisticexpialidocious

time python runReqestSemanticModelExperiments.py -u /media/storage/Experiments/DataSets/filtered/ISI_300KReq/ISI1 /media/storage/Experiments/DataSets/filtered/ISI_300KReq/ISI2 /media/storage/Experiments/DataSets/filtered/ISI_300KReq/ISI3 -o /media/storage/Experiments/SemanticModel/RF/ISI_300KReq/

time python runReqestSemanticModelExperiments.py -u /media/storage/Experiments/DataSets/filtered/ISI_500KReq/ISI1 -o /media/storage/Experiments/SemanticModel/RF/ISI_500KReq/


:<<supercalifragilisticexpialidocious
time python runAggressiveAttackerExperiment.py -u /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI1 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI2 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI3 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI4 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI5 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI6 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI7 -o /media/storage/Experiments/DynamicModel/TrainingPeriod/NewModel/trainTestWithAggressiveAttacker/100PercentTestAttacker/trainUAratio100/ISI_1MReq/ -r 100 -t 100

time python runAggressiveAttackerExperiment.py -u /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC1 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC2 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC3 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC4 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC5 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC6 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC7 -o /media/storage/Experiments/DynamicModel/TrainingPeriod/NewModel/trainTestWithAggressiveAttacker/100PercentTestAttacker/trainUAratio100/WC_100KReq/ -r 100 -t 100

time python runAggressiveAttackerExperiment.py -u /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI1 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI2 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI3 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI4 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI5 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI6 /media/storage/Experiments/DataSets/filtered/ISI_1MReq/ISI7 -o /media/storage/Experiments/DynamicModel/TrainingPeriod/NewModel/trainTestWithAggressiveAttacker/100PercentTestAttacker/trainUAratio1/ISI_1MReq/ -r 100 -t 1

time python runAggressiveAttackerExperiment.py -u /media/storage/Experiments/DataSets/filtered/ISI_100KReq/ISI1 /media/storage/Experiments/DataSets/filtered/ISI_100KReq/ISI2 /media/storage/Experiments/DataSets/filtered/ISI_100KReq/ISI3 /media/storage/Experiments/DataSets/filtered/ISI_100KReq/ISI4 /media/storage/Experiments/DataSets/filtered/ISI_100KReq/ISI5 /media/storage/Experiments/DataSets/filtered/ISI_100KReq/ISI6 /media/storage/Experiments/DataSets/filtered/ISI_100KReq/ISI7 -o /media/storage/Experiments/DynamicModel/TrainingPeriod/NewModel/trainTestWithAggressiveAttacker/100PercentTestAttacker/trainUAratio1/ISI_100KReq/ -r 100 -t 1

time python runAggressiveAttackerExperiment.py -u /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC1 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC2 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC3 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC4 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC5 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC6 /media/storage/Experiments/DataSets/filtered/WC_100KReq/WC7 -o /media/storage/Experiments/DynamicModel/TrainingPeriod/NewModel/trainTestWithAggressiveAttacker/100PercentTestAttacker/trainUAratio1/WC_100KReq/ -r 100 -t 1

time python runAggressiveAttackerExperiment.py -u /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC1 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC2 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC3 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC4 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC5 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC6 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC7 -o /media/storage/Experiments/DynamicModel/TrainingPeriod/NewModel/trainTestWithAggressiveAttacker/100PercentTestAttacker/trainUAratio1/WC_1MReq/ -r 100 -t 1

time python runAggressiveAttackerExperiment.py -u /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC1 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC2 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC3 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC4 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC5 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC6 /media/storage/Experiments/DataSets/filtered/WC_1MReq/WC7 -o /media/storage/Experiments/DynamicModel/TrainingPeriod/NewModel/trainTestWithAggressiveAttacker/100PercentTestAttacker/trainUAratio100/WC_1MReq/ -r 100 -t 100

supercalifragilisticexpialidocious

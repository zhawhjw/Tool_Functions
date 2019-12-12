from constructR import *
from matchingPersuit import *
from main import *

mainout = main('./main_userInfo_records.json','./main_diffusionInfo_records.json')
rout = parallel_r_main(mainout)
miniout = parallel_minimizer(rout)
print(miniout)
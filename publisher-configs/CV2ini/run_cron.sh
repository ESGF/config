cd /usr/local/src/config/publisher-configs/CV2ini
source /home/ames4/conda/etc/profile.d/conda.sh

fn=esg.cmip6.ini

dest=../ini/$fn


conda activate cvconv
python json2ini.py --project cmip6


tst=`diff $fn $dest | wc -l`

if [ $tst -ne 0 ] ; then
    cp $fn $dest
    git add $dest $fn
    git commit -m"Automated commit message triggered by CV change" 
    git push
else
    echo No changes
fi


import sys
from bscalculator import BowlingScoreCaliculator



# usageを出力して処理を終わる
def exit_usage():
    print('Usage: # python %s [json_file]' % argvs[0])
    quit()

# --メイン処理の実行--
# コマンドライン引数の取得、チェック
argvs = sys.argv
arglen = len(argvs)

if arglen != 2 :
    exit_usage()

# ファイル内容を文字列として読み込み
try:
    file = open(argvs[1],'r')
    json_data = file.read()
    file.close()
except:
    print('file load failed')
    quit()

# スコア計算用クラスを生成
bscalc = BowlingScoreCaliculator()

# スコア計算実施
scores = bscalc.calcScoreFromJson(json_data)

out_str_l1 = '|'
out_str_l2 = '|'
# TODO 適当すぎる出力
for score in scores :
    out_str_l2 = out_str_l2 + ' {0:03d} |'.format(score['score'])

print(out_str_l2)


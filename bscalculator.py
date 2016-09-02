import json
import time

# 定数(もどき)
# 通常のフレームの投球限界数
THROW_IN_NORMAL_FRAME = 2
# 最終フレームの投球限界数
THROW_IN_LAST_FRAME = 3

"""ボーリングのスコアを計算するクラスです"""
class BowlingScoreCaliculator :


    # コンストラクタ
    def __init__(self):
        pass

    # 空のスコアデータを生成
    def createEmptyScore(self):
        return {
            'pins': [],
            'mark': [],
            'score' : 0
        }

    # 投球結果のポイントを取得
    # ファールならポイントにしない
    def getPointOfThrow(self,game_data):
        if(game_data['foul'] == False):
            return game_data['pin']
        else :
            return 0

    # 投球データを時系列に整列しておく
    def sortGameData(self,json_data):
        # らむだ式でdateフィールドにキーソートをかける
        dtf = ''
        json_data['game_data'] = sorted(
            json_data['game_data'],
            key=lambda x : time.strptime(x['date'], "%Y-%m-%dT%H:%M:%S.%fZ")
        )

    # json文字列からスコアを計算し、スコア情報を返す
    def calcScoreFromJson(self,jsonstr):

        # jsonライブラリを利用し、json文字列を連想コンテナに変換する
        json_data = json.loads(jsonstr)

        # 先にデータを時系列に並べ替える
        self.sortGameData(json_data)

        # フレーム数、ピン数を保持
        frames = json_data['frame']
        pin_max = json_data['pin_max']
        all_throw_count = len(json_data['game_data'])

        # スコアデータの出力用の配列を保持する
        gamescores = []

        frame_cnt = 0
        throw_cnt = 0

        # 先頭の投球データから順にゲームを評価
        for game_data in json_data['game_data'] :
            # フレームのスコアオブジェクトがなければ作る
            if(len(gamescores)-1 < frame_cnt) : gamescores.append(self.createEmptyScore())

            # 倒した有効なピンの数を取得し投球加算
            pin = self.getPointOfThrow(game_data)
            gamescores[frame_cnt]['pins'].append(pin)
            throw_cnt += 1

            # 直前のフレームのスコア
            prev_score = 0 if frame_cnt == 0 else gamescores[frame_cnt-1]['score']

            # フレームが終了したかフラグを宣言
            is_frame_end = False

            # 最後のフレームか
            is_last_frame = frame_cnt == frames-1

            # このフレーム内で倒したピンの合計をとる
            pins_in_frame = sum(gamescores[frame_cnt]['pins'])

            # 全体の投球インデックス(0オリジン)
            throw_index_in_all = json_data['game_data'].index(game_data)

            if not is_last_frame:
                # 通常フレーム
                if (pins_in_frame >= pin_max or throw_cnt >= THROW_IN_NORMAL_FRAME) :
                    # すべてのピンを倒した、もしくは2投した
                    # 最終フレーム以外ならばフレーム終了
                    is_frame_end = True

                    # ストライク
                    if (throw_cnt == 1) :
                        # 先の2投目までを加算。2投先が無ければスコアの計算は不能
                        if(throw_index_in_all < all_throw_count-2) :
                            gamescores[frame_cnt]['score'] = prev_score + pins_in_frame + \
                                                             self.getPointOfThrow(json_data['game_data'][throw_index_in_all + 1]) + \
                                                             self.getPointOfThrow(json_data['game_data'][throw_index_in_all + 2])
                    # スペア
                    elif(pins_in_frame >= pin_max) :
                        # 先の1投目までを加算。1投先が無ければスコアの計算は不能
                        if(throw_index_in_all < all_throw_count-1) :
                            gamescores[frame_cnt]['score'] = prev_score + pins_in_frame + \
                                                             self.getPointOfThrow(json_data['game_data'][throw_index_in_all + 1])
                    # その他
                    else :
                        # そのままスコアを加算
                        gamescores[frame_cnt]['score'] = prev_score + pins_in_frame
            else :
                # 最終フレーム
                # 最終フレームは2投目までにストライクかスペア = 2投の合計がピン最大数以上なら3投可能
                # それ以下は2投で終わり
                if (throw_cnt == THROW_IN_LAST_FRAME-1 and pins_in_frame < pin_max) :
                    # ストライクもスペアも達成していないので終わり。
                    is_frame_end = True
                elif (throw_cnt == THROW_IN_LAST_FRAME):
                    # それ以外で3投したら終了
                    is_frame_end = True
                if is_frame_end :
                    # 最終フレームが終わったらフレーム内の合計値を単純加算
                    # TODO なんか自信ない...
                    gamescores[frame_cnt]['score'] = prev_score + pins_in_frame

            # フレームが終了した場合、投球カウントクリア、フレームを進める
            if is_frame_end:
                throw_cnt = 0
                frame_cnt += 1
        pass

        return gamescores

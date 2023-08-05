# -*- encoding:utf-8 -*-
'''
将OCR结果与底稿目录进行匹配
'''
import datetime
import jieba
import pandas as pd
from gensim import corpora, models, similarities
import pickle
import random
from Levenshtein import jaro, distance
import os
from settings import similarity, difference
import numpy as np
# def writeDictionary(textList):
#     texts1 = textList
#     texts = [jieba.lcut(text.replace(" ", "")) for text in texts1]
#     #基于文本来建立词典，并保存在词典中
#     dictionary = corpora.Dictionary(texts)
#     os.path.abspath(__file__)
#     dictionary.save("dictionary.dict")
#     # print(dictionary.token2id)
#     # print(type(dictionary.token2id))
#     print(len(dictionary.token2id))
#     #创建语料库并保存
#     corpus = [dictionary.doc2bow(text) for text in texts]
#     with open("corpus.pickle", "wb") as f:
#         f.write(pickle.dumps(corpus))
#     #传入语料库训练模型
#     tfidf = models.TfidfModel(corpus)
#     #保存模型
#     tfidf.save("tfidf.model")


# #将词典保存到dict文件夹中
# def getTextList():
#     df = pd.read_excel(filepath, sheet_name="Sheet1", engine="openpyxl",header=None)
#
#     # print(df)
#     # print(df.iloc[0,:])
#     textList = df.iloc[:, 1]
#     textList = textList.dropna()
#     # print(textList)
#     return textList
def getMatchList(matchfilePath, index=1, sheet_name = "Sheet1"):
    df = pd.read_excel(matchfilePath, sheet_name=sheet_name, engine="openpyxl", header=None)
    df.replace(np.nan, '', inplace=True)
    matchList = df.iloc[:, index-1] + df.iloc[:, index] + df.iloc[:, index+1]
    # matchList = matchList.dropna()

    return matchList

'''
param: FileNameList: 文件名列表
param: matchlist为OCR列表
param: pageList：页码列表
param: minScoreList：最小置信度列表
param: Avg_socreList: 平均置信度列表
param: shotValuesList 为底稿目录列表
param:shortlen: 字符串长度
param: filename: 要保存的文件名
'''
#FileNameList, OcrResultList, pageList, minScoreList, Avg_socreList,
#读取dict文件中保存的数据
def loadDictiloc(FileNameList,matchlist, pageList, minScoreList, Avg_socreList, shortValuesList, shortlen, filename):

    #当前文件所处的绝对路径
    absPath = os.path.abspath(__file__)
    #长文本字得到匹配后的结果，再使用短文本匹配的方法再次进行相似度匹配。并保存执行结果的相似度
    #长文本字得到匹配后的结果，再使用短文本匹配的方法再次进行相似度匹配。并保存执行结果的相似度
    firstSimilaritylist = []
    secoundSimilaritylist = []
    thirdSimilaritylist = []
    #文本长度列表用于判断短文本还是长文本
    textkenKist = []
    #判断相似度索引和原文本索引是否相等
    firstSameCode = []
    secoundSameCode = []
    thirdSameCode =[]
    fourthSameCode = []
    fifthSameCode = []
    #匹配值列表
    scoreList = []
    #所在索引的列表
    indexList = []
    #匹配到相似关键字的列表
    matchwordlist = []
    #匹配的原字符串
    baseWordList = []
    #第二-五大相似度的字符串匹配到的字符串的列表
    secondBaseWordList = []
    thirdBaseWordList = []
    fourthBaseWordList = []
    fifthBaseWordList = []
    #第二-五大相似度的列表
    secondIndexList = []
    thirdIndexList = []
    fourthIndexList = []
    fifthIndexList = []
    #相似度第二-五大的分数
    secoundScoreList = []
    thirdScoreList = []
    fourthScoreList = []
    fifthScoreList = []
    #创建字典
    absPath.replace('saveLoad.py', "dictionary.dict")
    # dictionary = corpora.Dictionary.load("dictionary.dict")
    dictionary = corpora.Dictionary.load(absPath.replace('saveLoad.py', "dictionary.dict"))
    print(dictionary)
    #随机替换的字符串列表
    randomWordlist = []
    #被替换字符串的列表
    replaceWordList = []
    #替换后的字符串
    afterReplacelist = []
    # 获取字典特征数
    num_features = len(dictionary.token2id)
    #获取字典中的包含的字的列表：
    wordList = list(dictionary.token2id.keys())
    print(wordList)
    #是否匹配成功的列表
    IsMatchList = []

    #获取语料库


    # with open("corpus.pickle", "rb") as f:
    with open(absPath.replace('saveLoad.py', "corpus.pickle"), "rb") as f:
        corpus = pickle.load(f)
        print(corpus)
        print(type(corpus))
    #加载模型
    # tfidf = models.TfidfModel.load('tfidf.model')
    tfidf = models.TfidfModel.load(absPath.replace('saveLoad.py', 'tfidf.model'))

    #第一次的匹配列表
    old_time = datetime.datetime.now()
    wordList = [i for i in wordList if len(i) == 1 and '\u0e00' <= i <= '\u9fa5'  and i not in ["》", '、',"“", "《", "”"]]
    print(wordList)
    for keyword in matchlist:
        # print(wordList)
        # if '重大股权变动涉及的政府批准文件、产权确认文件' in keyword:
        #     print(keyword)
        #按文本长度来对文本内容进行不同的操作
        if len(keyword) > shortlen:
            oldkeyword = keyword
            new_vec = dictionary.doc2bow(jieba.lcut(keyword))

            # 相似度计算
            index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features)
            # print('\nTF-IDF模型的稀疏向量集：')
            # for i in tfidf[corpus]:
            #     print(i)
            # print('\nTF-IDF模型的keyword稀疏向量：')
            # print(tfidf[new_vec])
            # print('\n相似度计算：')
            #匹配度的列表
            # print(tfidf[new_vec])
            sim = index[tfidf[new_vec]]
            #保存原始识别度的列表，在后面可能会需要修改其中的内容来保证不重复
            simList = list(sim)

            # print(sim)
            # print(max(sim) )
            #最大相似度值列表
            scoreList.append(max(sim))
            # print(keyword)
            # print(index(max(sim)))
            # print(corpus[index(max(sim))])
            # print(corpus[simList.index(max(sim))])
            # baseWord = "".join([dictionary[i[0]] for i in corpus[simList.index(max(sim))]])/\
            #最大相似度匹配到内容列表
            baseWordList.append(matchlist[simList.index(max(sim))])

            '''
            将获取过相似度的列相似度设置为aa
            '''
            # 最大相似度索引列表
            IndexList = simList.copy()
            IndexList.sort(reverse=True)
            indexList.append(simList.index(max(sim)))
            if simList.index(max(sim)) == matchlist.index(oldkeyword):
                firstSameCode.append("True")
            else:
                firstSameCode.append("False")
            firstSame = str(jaro(keyword, matchlist[simList.index(max(sim))])) + keyword + "--"+ matchlist[simList.index(max(sim))]
            firstSimilaritylist.append(firstSame)
            simList[simList.index(max(sim))] = "aa"
            # print(IndexList.sort(reverse=True))
            #获取第二大相似度的值
            secondScore = IndexList[1]
            #第二大相似度的值列表
            secoundScoreList.append(secondScore)
            # print(simList.index(secondScore))
            #第二大相似度的索引列表
            secondIndexList.append(simList.index(secondScore))
            #第二大相似度匹配到内容列表
            secondBaseWordList.append(matchlist[simList.index(secondScore)])
            #第二大相似度内容进行jaro匹配操作
            secoundSame = str(jaro(keyword, matchlist[simList.index(secondScore)])) + keyword + "--"+ matchlist[simList.index(secondScore)]
            secoundSimilaritylist.append(secoundSame)
            if simList.index(secondScore) == matchlist.index(oldkeyword):
                secoundSameCode.append("True")
            else:
                secoundSameCode.append("False")
            '''
                        将获取过相似度的列相似度设置为aa
            '''
            simList[simList.index(secondScore)] = "aa"
            thirdScore = IndexList[2]
            thirdScoreList.append(thirdScore)
            thirdIndexList.append(simList.index(thirdScore))
            thirdBaseWordList.append(matchlist[simList.index(thirdScore)])
            #第三大相似度内容进行jaro匹配操作
            thirdSame  = str(jaro(keyword, matchlist[simList.index(thirdScore)])) + keyword + "--"+ matchlist[simList.index(thirdScore)]
            thirdSimilaritylist.append(thirdSame )
            if simList.index(thirdScore) == matchlist.index(oldkeyword):
                thirdSameCode.append("True")
            else:
                thirdSameCode.append("False")
            '''
                                    将获取过相似度的列相似度设置为aa
            '''
            simList[simList.index(thirdScore)] = "aa"
            fourthScore = IndexList[3]
            fourthScoreList.append(fourthScore)
            fourthIndexList.append(simList.index(fourthScore))
            fourthBaseWordList.append(matchlist[simList.index(fourthScore)])
            if simList.index(fourthScore) == matchlist.index(oldkeyword):
                fourthSameCode.append("True")
            else:
                fourthSameCode.append("False")
            '''
                                                将获取过相似度的列相似度设置为aa
            '''
            simList[simList.index(fourthScore)] = "aa"
            fifthScore = IndexList[4]
            fifthScoreList.append(fifthScore)
            fifthIndexList.append(simList.index(fifthScore))
            fifthBaseWordList.append(matchlist[simList.index(fifthScore)])
            if simList.index(fifthScore) == matchlist.index(oldkeyword):
                fifthSameCode.append("True")
            else:
                fifthSameCode.append("False")
            '''
                                                            将获取过相似度的列相似度设置为aa
            '''
            simList[simList.index(fifthScore)] = "aa"
            #判断
            # for i in range(len(sim)):
            #     print('第', i+1, '句话的相似度为：', sim[i])

        #进行匹配短文本内容
        else:
            firstSimilaritylist.append("11")
            secoundSimilaritylist.append("22")
            thirdSimilaritylist.append("33")
            #这里对匹配的列表进行了复制
            matchlistCopy = shortValuesList.copy()
            # 匹配相似度值的列表
            shortscoreList = []
            # 短文本样本的列表`
            xlist = []
            for x in shortValuesList:
                # 通过Levenshtein中的jaro判断相似度
                # if '重大股权变动涉及的政府批准文件、产权确认文件' in x:
                #     print(x)
                # print(keyword)
                # print(x)
                shortscoreList.append(jaro(keyword.replace(" ", ""), x.replace(" ","")))


            #     xlist.append(x)
            # print(xlist)
            # print(shortscoreList)
            # 复制分数列表用于之后的提取操作
            scoreListCopy = shortscoreList.copy()
            shortscoreList.sort(reverse=True)
            # print(shortValuesList)
            # print(shortscoreList)
            previousnumber = 0
            afterReplacelist.append(keyword)

            for i in range(5):
                if i >= 1 and shortscoreList[i] == shortscoreList[i - 1]:
                    # 如果存在相似度相同的情况，修改数据列表中的内容防止再次匹配
                    scoreListCopy[previousnumber] = "c"
                #获取分数在原生成分数列表中所处的位置
                scoreIndex = scoreListCopy.index(shortscoreList[i])
                #要修改分数列表中对应分数的位置
                previousnumber = scoreIndex

                #匹配值对应在整个列表中值的位置
                # print())
                #第一大相似度内容
                if i == 0:
                    #匹配到的分数 scoreList为排序后的分数列表
                    # print(shortscoreList)
                    # print(shortscoreList[0])
                    scoreList.append(shortscoreList[0])
                    #匹配到的索引
                    indexList.append(matchlistCopy.index(shortValuesList[scoreIndex]))

                    # 匹配到值
                    baseWordList.append(shortValuesList[scoreIndex])
                    # if matchlistCopy.index(oldkeyword) == matchlistCopy.index(shortValuesList[scoreIndex]):
                    #     firstSameCode.append("True")
                    # else:
                    #     firstSameCode.append("False")
                    matchlistCopy[matchlistCopy.index(shortValuesList[scoreIndex])] = "aa"


                elif i == 1:

                    secoundScoreList.append(shortscoreList[i])
                    # 匹配到的索引
                    secondIndexList.append(matchlistCopy.index(shortValuesList[scoreIndex]))
                    # 匹配到值
                    secondBaseWordList.append(shortValuesList[scoreIndex])
                    # if matchlist.index(oldkeyword) == matchlistCopy.index(shortValuesList[scoreIndex]):
                    #     secoundSameCode.append("True")
                    # else:
                    #     secoundSameCode.append("False")
                    matchlistCopy[matchlistCopy.index(shortValuesList[scoreIndex])] = "aa"


                elif i == 2:
                    thirdScoreList.append(shortscoreList[i])
                    # 匹配到的索引
                    thirdIndexList.append(matchlistCopy.index(shortValuesList[scoreIndex]))
                    # 匹配到值
                    thirdBaseWordList.append(shortValuesList[scoreIndex])
                    # if matchlist.index(oldkeyword) == matchlistCopy.index(shortValuesList[scoreIndex]):
                    #
                    #     thirdSameCode.append("True")
                    # else:
                    #     thirdSameCode.append("False")
                    matchlistCopy[matchlistCopy.index(shortValuesList[scoreIndex])] = "aa"

                elif i == 3:
                    fourthScoreList.append(shortscoreList[i])
                    # 匹配到的索引
                    fourthIndexList.append(matchlistCopy.index(shortValuesList[scoreIndex]))
                    # 匹配到值
                    fourthBaseWordList.append(shortValuesList[scoreIndex])
                    # if matchlist.index(oldkeyword) == matchlistCopy.index(shortValuesList[scoreIndex]):
                    #     fourthSameCode.append("True")
                    # else:
                    #     fourthSameCode.append("False")
                    matchlistCopy[matchlistCopy.index(shortValuesList[scoreIndex])] = "aa"

                else:
                    fifthScoreList.append(shortscoreList[i])
                    # 匹配到的索引
                    fifthIndexList.append(matchlistCopy.index(shortValuesList[scoreIndex]))
                    # 匹配到值
                    fifthBaseWordList.append(shortValuesList[scoreIndex])
                    # if matchlist.index(oldkeyword) == matchlistCopy.index(shortValuesList[scoreIndex]):
                    #     fifthSameCode.append("True")
                    # else:
                    #     fifthSameCode.append("False")
                    matchlistCopy[matchlistCopy.index(shortValuesList[scoreIndex])] = "aa"

    for index in range(len(scoreList)):
        #判断第一个元素是否大于阈值，并且匹配到的第一个元素和第二个元素
        if scoreList[index] >= similarity and scoreList[index] - secoundScoreList[index] >= difference:
            IsMatchList.append(baseWordList[index])
        else:
            IsMatchList.append("")


    '''
    firstSimilaritylist, secoundSimilaritylist, thirdSimilaritylist是判断长字符串，判断还是短字符串判断
    '''
    # merge = pd.DataFrame(data=[matchlist,scoreList,baseWordList,secondIndexList, secoundScoreList, secondBaseWordList,
    #                            thirdIndexList,thirdScoreList, thirdBaseWordList, fourthIndexList, fourthScoreList, fourthBaseWordList, fifthIndexList, fifthScoreList, fifthBaseWordList,IsMatchList,
    #                            ],
    #                      index=['匹配字符',   "相似度", "所匹配的字符串","第二大相似度索引列表", "第二大相似度列表", "第二大相似度匹配内容列表",
    #                             "第三大相似度索引列表", "第三大相似度列表", "第三大相似度匹配内容列表", "第四大相似度索引列表", "第四大相似度列表", "第四大相似度匹配内容列表",
    #                             "第五大相似度索引列表", "第五大相似度列表", "第五大相似度匹配内容列表", "匹配到的内容", ]).T
    merge = pd.DataFrame(data=[FileNameList, matchlist, pageList, minScoreList, Avg_socreList,
                               scoreList,baseWordList, secoundScoreList, secondBaseWordList,
                               thirdScoreList, thirdBaseWordList,  fourthScoreList, fourthBaseWordList,  fifthScoreList, fifthBaseWordList,IsMatchList
                               ],
                         index=['文件名', 'OCRtext', "页码", "下限文本置信度", "平均文本置信度",
                                "第一大相似度列表", "所匹配的字符串", "第二大相似度列表", "第二大相似度匹配内容列表",
                                "第三大相似度列表", "第三大相似度匹配内容列表", "第四大相似度列表", "第四大相似度匹配内容列表",
                                "第五大相似度列表", "第五大相似度匹配内容列表", "匹配到的内容"]).T

    # print(merge)
    # merge.to_excel(filename, sheet_name = 'Sheet1')
    # new_time = datetime.datetime.now()
    # print(new_time-old_time)
    return merge




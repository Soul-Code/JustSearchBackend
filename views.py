from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, Answer, UserData, Team, TimeTable
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.core import serializers
import django.utils.timezone as timezone

import time
import json
import base64
import random

import requests

# from bs4 import BeautifulSoup

session = requests.Session()
url_login = 'https://www.shuhelper.cn/api/users/login/'
headers = {'Accept': 'application/json, text/plain, */*',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           'Cache-Control': 'no-cache',
           'Connection': 'Keep-Alive',
           'Content-Type': 'application/json;charset=UTF-8',
           'Host': 'www.shuhelper.cn',
           'Origin': 'https://www.shuhelper.cn',
           'Pragma': 'no-cache',
           'Referer': 'https://www.shuhelper.cn/login',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/69.0.3497.100 Safari/537.36'}


# 报名系统api
def index(request, string=''):
    print(string)
    # if string == 'Beta':
    userid = request.session.get('userid')
    msg = {}
    if userid:
        user = UserData.objects.filter(id=userid)
        if user.exists():
            user = user.first()
            # todo 通知的处理逻辑太过于智障
            # 团体赛通知
            # if user.isPromoted:
            #     msg = {'msg': '恭喜你成功晋级！/恭喜你成功晋级，请到1106休息等待最终的决赛！'}
            # else:
            #     msg = {'msg': '还有复活赛！/很遗憾你没有成功晋级，但是还有复活赛，还有机会进入决赛！'}

            # 复活赛通知
            # if user.isPromoted:
            #     msg = {'msg': '恭喜你成功晋级！/恭喜你成功晋级，请到指定机房参加最终的决赛！'}
            # else:
            #     msg = {'msg': '很遗憾！/你与决赛失之交臂……'}

            # 个人赛通知
            # if user.isPromoted:
            #     msg = {'msg': '等待结果！/请等待工作人员对比赛情况进行最终审核！'}
            # else:
            #     msg = {'msg': '等待结果！/请等待工作人员对比赛情况进行最终审核……'}

    return render(request, 'JustSearch/index.html', msg)
    # return render(request, 'JustSearch/index.html')
    # return HttpResponse('不在比赛时间')


@csrf_exempt
def login_view(request):
    res_data = {'isOk': False, 'errmsg': '未知错误'}
    if request.method == 'POST' and request.is_ajax():
        if not request.body.decode():
            json_data = json.dumps(res_data)
            return HttpResponse(json_data, content_type="application/json")
        data = json.loads(request.body.decode())
        if data.get('isAgree'):
            # 必须同意比赛准则
            username = data.get('username')
            psword = data.get('password')

            if username and psword:
                # 登陆
                #  检查数据库有没有该用户
                user = UserData.objects.filter(
                    stdid=username,
                )
                if user.exists():
                    # 找到该用户 验证密码
                    user = user.first()
                    print('查到', user)
                    res = login_std(username, psword)
                    if not res:
                        # 密码错误
                        res_data['errmsg'] = '用户名或密码错误'
                    else:
                        # 密码验证成功
                        # 绑定到session
                        request.session['userid'] = user.id
                        res_data['isOk'] = True
                        res_data['userInfo'] = getUserInfo(user.id)
                else:
                    # 没有找到该用户 验证用户名和密码创建用户
                    res = login_std(username, psword)
                    if res:
                        res_data['errmsg'] = 'ok'
                        res_data['isOk'] = True
                        res_data['name'] = res.get('name')
                        print('登陆成功', res)
                        # 写入数据库
                        user_now = UserData.objects.create(
                            stdid=username,
                            name=res.get('name')
                        )
                        request.session['userid'] = user_now.id

                    else:
                        print('登陆失败')
                        res_data['errmsg'] = '用户名或密码错误'
            else:
                res_data['errmsg'] = '用户名或密码为空'
        else:
            res_data['errmsg'] = '必须同意比赛准则'
        return JsonResponse(res_data)


@csrf_exempt
def new_team(request):
    # todo 这边截止报名是一次性的……待更正……
    res_data = {'isOk': False, 'errmsg': '报名已经截止！'}
    if request.method == 'POST':
        # user = isAuthed(request)
        # if not user:
        #     res_data['errmsg'] = '获取授权信息失败'
        #     JsonResponse(res_data)
        # data = json.loads(request.body.decode())
        # teamname = data.get('teamname')
        # if Team.objects.filter(name=teamname).exists():
        #     res_data['errmsg'] = '队伍名称已存在'
        # else:
        #     print(user, '创建队伍', data)
        #     if user.team:
        #         res_data['errmsg'] = '你已经有队伍了哟'
        #     else:
        #         user.team = Team.objects.create(
        #             name=data.get('teamname'),
        #             leader=user.name
        #         )
        #         user.save()
        #         request.session['teamid'] = user.team.id
        #
        #         res_data['isOk'] = True
        # res_data['userInfo'] = getUserInfo(user.id)
        return JsonResponse(res_data)


@csrf_exempt
def get_team(request):
    res_data = {'isOk': False, 'errmsg': '未知错误'}
    if request.method == 'POST':
        userid = request.session.get('userid')
        if userid:
            if UserData.objects.filter(id=userid).exists():
                res_data['isOk'] = True
                res_data['userInfo'] = getUserInfo(userid)
                print(res_data['userInfo'])
        # 已经获得登陆授权~
        json_data = json.dumps(res_data)
        return HttpResponse(json_data, content_type="application/json")


@csrf_exempt
def register(request):
    res_data = {'isOk': False, 'errmsg': '未知错误'}
    if request.method == 'POST' and request.is_ajax():
        userid = request.session.get('userid')
        user = UserData.objects.filter(id=userid)
        if not user.exists():
            print('用户不存在')
            res_data['errmsg'] = 'User Not Found'
            json_data = json.dumps(res_data)
            return HttpResponse(json_data, content_type="application/json")
        user = user.first()
        if not request.body.decode():
            print('没有收到信息')
            res_data['errmsg'] = 'Msg Not Found'
            json_data = json.dumps(res_data)
            return HttpResponse(json_data, content_type="application/json")
        data = json.loads(request.body.decode())
        qq = data.get('qq')
        tel = data.get('tel')
        if qq and tel and user:
            user.qq = qq
            user.tel = tel
            user.save()
            res_data['isOk'] = True
            res_data['userInfo'] = getUserInfo(userid)
        json_data = json.dumps(res_data)
        return HttpResponse(json_data, content_type="application/json")


@csrf_exempt
def get_rank(request):
    res_data = {'isOk': False, 'errmsg': '未知错误'}
    if request.method == 'POST':
        userid = request.session.get('userid')
        if userid:
            data = json.loads(request.body.decode())
            if data.get('who') == 'team':
                res_data['isOk'] = True
                res_data['teams'] = list(
                    Team.objects.all().order_by('-score', 'finish_time','-id')[:25].values_list('id', 'name', 'score'))
                res_data['users'] = list(
                    UserData.objects.all().order_by('-score', 'finish_time','-id')[:15].values_list('id', 'name', 'score'))
        # 已经获得登陆授权~
        json_data = json.dumps(res_data)
        return HttpResponse(json_data, content_type="application/json")


@csrf_exempt
def find_team(request):
    res_data = {'isOk': False, 'errmsg': '未知错误'}
    if request.method == 'POST':
        userid = request.session.get('userid')
        if userid:
            data = json.loads(request.body.decode())
            team_find = data.get('teamfind')
            print(team_find)
            # if(team_find)
            if team_find.isdigit():
                team1 = Team.objects.filter(id=team_find)
                if team1.exists():
                    team1 = team1.first()
                    # if len(team1.mems.all()) < 3:
                    res_data['team'] = {'name': team1.name, 'id': team1.id, 'leader': team1.leader}
                    res_data['isOk'] = True
            team2 = Team.objects.filter(Q(name__contains=team_find) | Q(leader__contains=team_find))
            if team2.exists() and not res_data['isOk']:
                team2 = team2.first()
                # if len(team2.mems.all()) < 3:
                res_data['team'] = {'name': team2.name, 'id': team2.id, 'leader': team2.leader}
                res_data['isOk'] = True
    json_data = json.dumps(res_data)
    return HttpResponse(json_data, content_type="application/json")


@csrf_exempt
def join_team(request):
    res_data = {'isOk': False, 'errmsg': '未知错误'}
    if request.method == 'POST':
        userid = request.session.get('userid')
        if userid:
            user = UserData.objects.filter(id=userid)
            if user.exists():
                user = user.first()
                data = json.loads(request.body.decode())
                teamid = data.get('id')
                team = Team.objects.filter(id=teamid).first()
                if len(team.mems.all()) >= 3:
                    res_data['errmsg'] = '队伍人数已满'
                elif isScored(team):
                    res_data['errmsg'] = '队伍已经开始答题'
                else:
                    user.team = team
                    user.save()
                    res_data['isOk'] = True
                    res_data['userInfo'] = getUserInfo(userid)
        # 已经获得登陆授权~
        json_data = json.dumps(res_data)
        return HttpResponse(json_data, content_type="application/json")


@csrf_exempt
def quit_team(request):
    res_data = {'isOk': False, 'errmsg': '未知错误'}
    if request.method == 'POST':
        userid = request.session.get('userid')
        if userid:
            user = UserData.objects.filter(id=userid)
            data = json.loads(request.body.decode())
            if user.exists() and data.get('id'):
                user = UserData.objects.filter(id=data.get('id')).first()
                teamid = user.team.id
                print(teamid)
                if isScored(Team.objects.get(id=teamid)):
                    res_data['errmsg'] = '队伍已经开始答题'
                else:
                    user.team = None
                    user.save()
                    res_data['isOk'] = True
                    res_data['userInfo'] = getUserInfo(userid)
        # 已经获得登陆授权~
        json_data = json.dumps(res_data)
        return HttpResponse(json_data, content_type="application/json")


def logout(request):
    request.session['userid'] = ''
    res_data = {'isOk': True}
    json_data = json.dumps(res_data)
    return HttpResponse(json_data, content_type="application/json")


@csrf_exempt
def del_team(request):
    res_data = {'isOk': False, 'errmsg': '无法完成操作'}
    team = Team()
    user = UserData()
    if request.method == 'POST':
        userid = request.session.get('userid')
        if userid:
            user = UserData.objects.get(id=int(userid))
            team = Team.objects.filter(leader=user.name)
            if team.exists():
                team = team.first()
                res_data['isOk'] = True
            else:
                res_data['errmsg'] = '你好像不是队伍的队长~'
        else:
            res_data['errmsg'] = '未找到用户'
        # 找到预备被删除的队伍~
        if res_data['isOk']:
            if isScored(team):
                res_data['errmsg'] = '队伍已经开始答题'
                res_data['isOk'] = False
            else:
                request.session['team'] = ''
                team_del = team
                team_del.delete()
                res_data['userInfo'] = getUserInfo(userid)
        json_data = json.dumps(res_data)
        return HttpResponse(json_data, content_type="application/json")


# 答题系统apis

@csrf_exempt
def get_questions(request, page_num=0):
    res_data = {'isOk': False, 'errmsg': '未知错误'}
    finished = False
    if request.method == 'POST':
        userid = request.session.get('userid')
        if userid:
            user = UserData.objects.select_related('team').filter(id=userid)
            if user.exists():
                user = user.first()
                stage = get_stage()
                seed = 0
                if stage:
                    if stage.name == '预选赛':
                        finished = user.team.isFinished
                        seed = user.team.id
                        pass
                    elif stage.name == '团队赛':
                        finished = user.team.isFinished
                        seed = user.team.id
                        pass
                    elif stage.name == '复活赛':
                        finished = user.isFinished
                        seed = user.id
                        pass
                    elif stage.name == '个人赛':
                        finished = user.isFinished
                        seed = user.id
                        pass
                else:
                    print('不在比赛时间')
                    res_data['errmsg'] = '不在比赛时间'
                    return HttpResponse(json.dumps(res_data).encode(), content_type="application/json")
                page_now = []
                res_data = {'isOk': False}
                # 遍历所有难度，每个难度分别随机出来指定数目的题目
                # 12  12  6
                #  0  10  0
                #  9  12  9
                diffs = [0, 1, 2]
                questions = []
                for diff in diffs:
                    questions_fliter = Question.objects.filter(stage__name=stage.name, difficulty=diff).order_by('id')
                    print('难度%d,筛选之前共有题目%d->   ' % (diff, questions_fliter.count()), end='')
                    for i in questions_fliter:
                        print(i.id, end=' ')
                    print()
                    random.seed(seed)
                    questions_fliter = list(questions_fliter)
                    questions_fliter = random.sample(questions_fliter, len(questions_fliter) // 2)
                    print('难度%d,筛选完了还有题目%d->   ' % (diff, len(questions_fliter)), end='')
                    for i in questions_fliter:
                        print(i.id, end=' ')
                    print()
                    questions += questions_fliter

                print('筛选完了总共还有题目%d->   ' % len(questions), end='')
                for i in questions:
                    print(i.id, end=' ')
                print()

                # questions = Question.objects.filter(stage__name=stage.name).order_by('id')
                # random.seed(user.team.id)
                # questions = list(questions)
                # questions = random.sample(questions, 30)

                pages = Paginator(questions, 10)
                print('一共有', pages.count, '题')
                print('一共有', pages.num_pages, '页')
                res_data['page_count'] = pages.count
                res_data['page_num_pages'] = pages.num_pages
                if page_num == 0:
                    res_data['isOk'] = True
                    page_num = 1
                    page_now = pages.page(page_num).object_list
                    answered_questions = 0
                    if stage.name in ['团队赛', '预选赛']:
                        answered_questions = Question.objects.filter(answer__user__team=user.team,
                                                                     stage=stage).distinct()
                    elif stage.name in ['复活赛', '个人赛']:
                        answered_questions = Question.objects.filter(answer__user=user, stage=stage).distinct()
                    answered_num = len(answered_questions)
                    res_data['answered_num_all'] = answered_num
                    res_data['userInfo'] = getUserInfo(user.id)
                elif page_num in pages.page_range:
                    page_now = pages.page(page_num).object_list
                    res_data['isOk'] = True
                else:
                    res_data['isOk'] = False
                    res_data['errmsg'] = '页码超出范围'
                if res_data['isOk']:
                    res_data['page_num'] = page_num
                    res_data['isFinished'] = finished

                    questions = json.loads(
                        serializers.serialize('json', page_now, fields=('question_text', 'choices', 'difficulty')))
                    # res_data['answered_choices'] = json.loads(
                    #     serializers.serialize('json',
                    #                           Answer.objects.filter(user__team=user.team,
                    #                                                 question__in=page_now).order_by('pub_time'),
                    #                           fields=('question_text', 'choices', 'difficulty')))
                    for i in range(len(questions)):
                        # 查看最近选项功能
                        if stage.name in ['团队赛', '预选赛']:
                            answers = Answer.objects.filter(user__team=user.team, question_id=questions[i]['pk'],
                                                            stage=stage)
                        elif stage.name in ['复活赛', '个人赛']:
                            print('个人赛')
                            answers = Answer.objects.filter(user=user, question_id=questions[i]['pk'],
                                                            stage=stage)

                        if answers.exists():
                            questions[i]['answered_num'] = answers.aggregate(Sum('pub_num')).get('pub_num__sum', 0)
                            questions[i]['answered_choices'] = answers.order_by('pub_time')[0].choose
                        else:
                            questions[i]['answered_num'] = 0
                            questions[i]['answered_choices'] = -1
                    res_data['questions'] = questions
            else:
                res_data['errmsg'] = '请登陆后再试'
    return JsonResponse(res_data)


@csrf_exempt
def get_stages(request):
    time_now = int(time.time())
    data = {'isOk': True, 'time_now': time_now}
    stages = TimeTable.objects.all().order_by('id')
    stages_data = json.loads(serializers.serialize('json', stages))
    stages_fields = []
    for i in range(len(stages)):
        data_temp = {
            'name': stages[i].name,
            'timeStart': get_time(stages[i].timeStart),
            'timeEnd': get_time(stages[i].timeEnd),
        }
        stages_fields.append(data_temp)
        stages_data[i]['fields'] = data_temp
    data['stages'] = stages_data
    if get_stage():
        data['stage'] = get_stage().id
    else:
        data['stage'] = 0
    return HttpResponse(json.dumps(data).encode(), content_type="application/json")


def add_time(user, stage, diff):
    if stage.name == '团队赛':
        user.team.add_time += 2
        user.team.save()
        pass
    elif stage.name == '复活赛':
        if diff >= 1:
            user.add_time += 2
            user.save()
    elif stage.name == '个人赛':
        user.add_time += pow(2, diff)
        user.save()


def add_score(user, stage, diff):
    if stage.name == '预选赛':
        user.team.score += 2
        user.team.save()
    elif stage.name == '团队赛':
        user.team.score += 2 * diff + 1
        print('加分' + str(2 * diff + 1))
        user.team.save()
    elif stage.name == '复活赛':
        user.score += 2
        user.save()
    elif stage.name == '个人赛':
        user.score += 3 * diff + 2
        user.save()


@csrf_exempt
def submit_answer(request):
    res_data = {'isOk': False, 'errmsg': '未知错误'}
    user = isAuthed(request)
    stage_type = ''
    if user:
        print(user, '身份验证成功')
        if not isTeamed(user):
            print('没有加入队伍')
            res_data['errmsg'] = '没有加入队伍'
            return JsonResponse(res_data)
        stage = get_stage()
        if not stage:
            print('不在比赛时间')
            res_data['errmsg'] = '不在比赛时间'
            return JsonResponse(res_data)
        if stage.name in ['团队赛', '预选赛']:
            stage_type = 'team'
        elif stage.name in ['复活赛', '个人赛']:
            stage_type = 'single'
        if user.team.isFinished and stage_type == 'team':
            print('已经完成比赛,禁止答题')
            res_data['errmsg'] = '禁止答题'
            return JsonResponse(res_data)
        if user.isFinished and stage_type == 'single':
            print('已经完成比赛,禁止答题')
            res_data['errmsg'] = '禁止答题'
            return JsonResponse(res_data)
        data = json.loads(request.body.decode())

        if data.get('allOk'):
            # 都答完了，计算罚时
            answered_question_num = 0
            if stage_type == 'team':
                answered_question_num = Question.objects.filter(answer__user__team=user.team, stage=stage).count()
            elif stage_type == 'single':
                answered_question_num = Question.objects.filter(answer__user=user, stage=stage).count()
                print(Question.objects.filter(answer__user=user, stage=stage), stage)

            # fixme 根据比赛场次计算已答题（team/singe
            question_num = Question.objects.filter(stage=stage).count() // 2
            print('answered_question_num', answered_question_num)
            print('question_num', question_num)
            if question_num <= answered_question_num:
                dt = timezone.now() - stage.timeStart

                def add(obj):
                    # 罚时计算函数
                    obj.finish_time = dt.total_seconds() / 60 + obj.add_time
                    obj.isFinished = True
                    obj.save()

                if stage_type == 'team':
                    add(user.team)
                elif stage_type == 'single':
                    add(user)
                # 已经完成比赛
                res_data['isOk'] = True
            else:
                res_data['errmsg'] = "请完成所有题目后再提交哟"
            return JsonResponse(res_data)

        pk = data.get('question_pk', -1)
        choice = data.get('choice', -1)
        print(data)
        if pk != -1 and choice != -1:
            # 传入答案合法
            choice_now = Answer.objects.filter(user=user, question_id=int(pk), stage=stage)
            answered_num = 0
            if stage_type == 'team':
                print('stage_type == "team"')
                team_answered = Answer.objects.filter(user__team=user.team, question_id=int(pk), stage=stage)
                answered_num = team_answered.aggregate(Sum('pub_num')).get('pub_num__sum', 0)
                if not answered_num:
                    answered_num = 0

            elif stage_type == 'single':
                print('stage_type == "single"')
                answered_num = choice_now.aggregate(Sum('pub_num')).get('pub_num__sum', 0)
                if not answered_num:
                    answered_num = 0
            question_answered = Question.objects.get(pk=pk)
            diff = question_answered.difficulty
            # 进入判题逻辑
            if choice_now.exists():
                # user已经答过一次了
                print('user已经答过一次了')
                choice_now = choice_now.first()
                # print(choice_now.pub_num)
                if answered_num <= 1:
                    # 队没答过
                    if question_answered.key == choice:
                        # 答对了
                        if not choice_now.isRight:
                            print('上次答错了这次答对了，加分')
                            choice_now.isRight = True
                            choice_now.save()
                            add_score(user, stage, diff)
                        else:
                            print('上次答对了这次答对了，不变（是谁两次提交一样的答案？）')
                    else:
                        # 答错了 先罚时再说
                        add_time(user, stage, diff)
                        # 看看上次怎么样呢
                        if not choice_now.isRight:
                            print('上次答错了这次答错了，只罚时')
                        else:
                            if stage.name == '预选赛':
                                user.team.score -= 2
                                user.team.save()
                            elif stage.name == '团队赛':
                                user.team.score -= 2 * diff + 1
                                user.team.save()
                            elif stage.name == '复活赛':
                                user.score -= 2
                                user.save()
                            elif stage.name == '个人赛':
                                user.score -= 3 * diff + 2
                                user.save()
                            choice_now.isRight = False
                            choice_now.save()
                            print('上次答对了这次答错了减分儿，罚时')
                    choice_now.pub_num = choice_now.pub_num + 1
                    choice_now.choose = choice
                    choice_now.save()
                    res_data['isOk'] = True
                else:
                    res_data['errmsg'] = '答题次数达到上限'
            else:
                # user没有答过
                print('user没有答过')
                if answered_num == 0:
                    if question_answered.key == choice:
                        # 答对了
                        add_score(user, stage, diff)
                        print('答对了，加分儿')
                    else:
                        # 答错了
                        add_time(user, stage, diff)
                        print('答错了，罚时')
                    res_data['isOk'] = True
                elif answered_num == 1:
                    team_answered = team_answered.first()
                    if question_answered.key == choice:
                        # 答对了
                        if not team_answered.isRight:
                            print('上次答错了这次答对了，加分')
                            add_score(user, stage, diff)
                        else:
                            print('上次答对了这次答对了，不变（是谁两次提交一样的答案？）')
                    else:
                        # 答错了 先罚时再说
                        add_time(user, stage, diff)
                        # 看看上次怎么样呢
                        if not team_answered.isRight:
                            print('上次答错了这次答错了，不做')
                        else:
                            if stage.name == '预选赛':
                                user.team.score -= 2
                                user.team.save()
                            elif stage.name == '团队赛':
                                user.team.score -= 2 * diff + 1
                                user.team.save()
                            elif stage.name == '复活赛':
                                user.score -= 2
                                user.save()
                            elif stage.name == '个人赛':
                                user.score -= 3 * diff + 2
                                user.save()
                            print('上次答对了这次答错了减分儿')
                    # choice_now.pub_num = choice_now.pub_num + 1
                    # choice_now.choose = choice
                    # choice_now.save()
                elif answered_num >= 2:
                    res_data['errmsg'] = '答题次数达到上限'
                    return JsonResponse(res_data)

                res_data['isOk'] = True
                Answer.objects.create(
                    user=user,
                    question=question_answered,
                    isRight=question_answered.key == choice,
                    choose=choice,
                    pub_num=1,
                    stage=stage
                )

                res_data['isOk'] = True
                print('首次答题成功')
        else:
            res_data['errmsg'] = '传入数据不合法'
    else:
        res_data['errmsg'] = '获取授权信息失败'
    return JsonResponse(res_data)
    # return HttpResponse(json.dumps(res_data).encode(), content_type="application/json")


# tools


def get_team_questions(question_id):
    print(question_id)


def get_stage():
    stages = TimeTable.objects.all().order_by('id')
    time_now = timezone.now()
    for stage in stages:
        if stage.timeStart <= time_now <= stage.timeEnd:
            return stage
    return None


def get_time(datetime):
    return int(time.mktime(timezone.localtime(datetime).timetuple()))


def isAuthed(request):
    if request.method == 'POST':
        userid = request.session.get('userid')
        if userid:
            user = UserData.objects.filter(id=userid)
            if user.exists():
                user = user.first()
                return user
    return None


def isTeamed(user):
    if user.team:
        return True
    else:
        return False


def isScored(team):
    if team.score > 0:
        return True
    else:
        return False


def getUserInfo(userid):
    user = UserData.objects.get(pk=userid)
    stage = get_stage()
    finished = False

    team = user.team
    team_data = {}
    if team:
        if stage:
            if stage.name == '预选赛':
                finished = user.team.isFinished
                pass
            elif stage.name == '团队赛':
                finished = user.team.isFinished
                pass
            elif stage.name == '复活赛':
                finished = user.isFinished
                pass
            elif stage.name == '个人赛':
                finished = user.isFinished
                pass
        mems_data = []
        mems = team.mems.all()
        # print(list(mems.values_list('id', 'name')))
        for mem in mems:
            mems_data.append({'id': mem.id, 'name': mem.name})
        team_data = {
            'id': team.id,
            'name': team.name,
            'score': team.score,
            'leader': team.leader,
            'mems': mems_data
        }
    if stage:
        print('1')
        return {
            'id': user.id,
            'name': user.name,
            'score': user.score,
            'tel': user.tel,
            'qq': user.qq,
            'stage': stage.pk,
            'team': team_data,
            'isFinished': finished
        }
    else:
        print('2')
        return {
            'id': user.id,
            'name': user.name,
            'score': user.score,
            'tel': user.tel,
            'qq': user.qq,
            'stage': 0,
            'team': team_data,
            'isFinished': finished
        }


def login_std(username='16122364', psword='123'):
    # res_pre = session.get(url_login)
    data = {
        'card_id': username,
        'password': psword,
    }

    res = session.post(url_login,
                       data=json.dumps(data), headers=headers)
    if res.status_code == 200:
        return json.loads(res.text)
    else:
        return False


def yxwh(request, txt):
    content = {'txt': txt}
    return render(request, 'JustSearch/yxwh.html', content)

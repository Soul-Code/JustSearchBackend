from django.contrib import admin
from .models import UserData, Question, Answer, Team, TimeTable, Choice

import django.utils.timezone as timezone

import time
import xlwt

# Register your models here.
admin.site.site_header = 'Just搜搜后台管理系统'
admin.site.site_title = 'Just搜搜后台管理系统'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    actions = ['rejudge']
    ordering = ['id']
    search_fields = ['question_text', 'id', 'choices']
    # list_display = ('id', 'question_text', 'choices', 'key', 'difficulty', 'answered_team_num', 'accuracy', 'stage')
    list_display = ('id', 'question_text', 'choices', 'key', 'difficulty', 'answered_team_num', 'stage')
    list_display_links = ('id', 'question_text',)
    preserve_filters = True

    # list_editable = ['name', 'leader', 'score']
    def rejudge(self, request, queryset):
        # print(queryset)
        for question in queryset:
            questions_answers = Answer.objects.filter(question=question)
            teams = Team.objects.filter(mems__answer__question=question)
            # print(len(team.distinct()), answers.count())
            for team in teams:
                team_answer = Answer.objects.filter(question=question, user__team=team).order_by('pub_time')[0]
                print(team_answer.choose, question.key, team_answer.isRight)
                if team_answer.isRight:
                    # 之前答对了
                    if team_answer.choose != question.key:
                        print(team.name, '减两分')
                        team.score += 2
                        team.save()
                else:
                    # 之前答错了
                    if team_answer.choose == question.key:
                        print(team.name, '加两分')
                        team.score += 2
                        team.save()
            for answer in questions_answers:
                if answer.choose == question.key:
                    answer.isRight = True
                else:
                    answer.isRight = False
                answer.save()
        self.message_user(request, "重新判题成功！嘤！你给我嘤！")

    def answered_team_num(self, obj):
        return len(Team.objects.filter(mems__answer__question=obj).distinct())

    def accuracy(self, obj):
        teams = Team.objects.filter(mems__answer__question=obj).distinct()
        all_team_num = teams.count()
        s = 0
        for team in teams:
            if Answer.objects.filter(user__team=team, question=obj).order_by('pub_time')[0].isRight:
                s += 1
        return '%f%%' % (s / all_team_num * 100)

    rejudge.short_description = "重新判题"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    ordering = ['-id']

    search_fields = ['user__name', 'question__question_text', 'user__team__name']
    list_filter = ('choose', 'pub_time', 'stage')
    list_display = ('id', 'stage', 'pub_time', 'team', 'user', 'choose', 'isRight', 'pub_num', 'question',)
    time_hierarchy = 'pub_time'

    def team(self, obj):
        if Team.objects.filter(mems=obj.user):
            return Team.objects.filter(mems=obj.user)[0].name
        else:
            return 'NaN'

    team.short_description = "答题队"


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ['name']
    actions = ['anti_cheat', 'reset', 'Promoted', 'UnPromoted']
    list_filter = ('isFinished',)
    list_display = (
        'id', 'name', 'leader', 'mems', 'score', 'pub_time', 'add_time', 'finish_time', 'answered_questions',
        'isFinished')
    # list_display_links = ('name', 'leader',)
    list_editable = ['name', 'leader', 'score']

    def answered_questions(self, obj):
        return Question.objects.filter(answer__user__team=obj).distinct().count()

    def mems(self, obj):
        data = ''
        for user in UserData.objects.filter(team=obj).values_list('name'):
            data += user[0] + ' '
        return data

    def get_time(self, datetime):
        return int(time.mktime(timezone.localtime(datetime).timetuple()))

    def anti_cheat(self, request, queryset):
        print(queryset)
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('teams')
        text = ['id', 'name', 'score', 'start', 'end', 'delta', 'answers']
        for i in range(7):
            worksheet.write(0, i, text[i])
        teams = queryset
        questions = Question.objects.all().order_by('id')
        choices = ['' for i in range(len(teams))]
        for j in range(len(teams)):
            worksheet.write(j + 1, 0, teams[j].id)
            worksheet.write(j + 1, 1, teams[j].name)
            worksheet.write(j + 1, 2, teams[j].score)
            for i in range(len(questions)):
                choose = \
                    Answer.objects.filter(user__team=teams[j], stage__name='预选赛', question=questions[i]).order_by(
                        'pub_time')
                if choose:
                    choose = choose[0].choose
                    choices[j] += str(chr(choose + 65))
                else:
                    choices[j] += '_'

            worksheet.write(j + 1, 6, choices[j])
            answers = Answer.objects.filter(user__team=teams[j], stage__name='预选赛').order_by('pub_time')
            worksheet.write(j + 1, 3, str(answers[0].pub_time))
            worksheet.write(j + 1, 4, str(answers[len(answers) - 1].pub_time))

            if teams[j].id == 107:
                worksheet.write(j + 1, 5, 240335.888399)
            else:
                worksheet.write(j + 1, 5, (answers[len(answers) - 1].pub_time - answers[0].pub_time).total_seconds())
        print(choices)

        workbook.save('JustSearch/teams.xls')
        self.message_user(request, "成功导出反作弊数据！给我嘤！")

    def reset(self, request, queryset):
        queryset.update(score=0, add_time=0, finish_time=0, isFinished=False)
        self.message_user(request, "成功reset %d 个队伍！给我嘤！" % len(queryset))

    def Promoted(self, request, queryset):
        for team in queryset:
            users = UserData.objects.filter(team=team)
            users.update(isPromoted=True)
        self.message_user(request, "成功晋级 %d 个队伍！给我嘤！" % len(queryset))

    def UnPromoted(self, request, queryset):
        for team in queryset:
            users = UserData.objects.filter(team=team)
            users.update(isPromoted=False)
        self.message_user(request, "成功反晋级 %d 个队伍！给我嘤！" % len(queryset))

    anti_cheat.short_description = '反作弊审查'
    reset.short_description = '重置队伍'
    Promoted.short_description = '给我晋级'
    UnPromoted.short_description = '给我反晋级'


@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'timeStart', 'timeEnd')
    # list_display_links = ('name', 'leader',)
    list_editable = ['name', 'timeStart', 'timeEnd']


@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    actions = ['reset', 'Promoted', 'UnPromoted', 'answered']
    list_display = (
        'id', 'name', 'stdid', 'score', 'add_time', 'finish_time', 'qq', 'tel', 'team_name', 'isPromoted', 'isFinished',
        'pub_time')
    list_display_links = ('id', 'name', 'stdid')
    list_editable = ['score', 'isPromoted']
    fields = (('name', 'stdid'), ('qq', 'tel'), 'score', 'team', 'isPromoted')

    def reset(self, request, queryset):
        queryset.update(score=0, add_time=0, finish_time=999, isFinished=False)
        self.message_user(request, "成功reset %d 个选手！给我嘤！" % len(queryset))

    def Promoted(self, request, queryset):
        queryset.update(isPromoted=True)
        self.message_user(request, "成功晋级 %d 个选手！给我嘤！" % len(queryset))

    def UnPromoted(self, request, queryset):
        queryset.update(isPromoted=False)
        self.message_user(request, "成功反晋级 %d 个选手！给我嘤！" % len(queryset))

    def team_name(self, obj):
        if obj.team:
            return obj.team.name
        else:
            return None

    def answered(self, request, queryset):
        print(queryset)
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('users')
        text = ['id', '姓名', '学号', '答题数量']
        for i in range(3):
            worksheet.write(0, i, text[i])
        users = queryset

        for i in range(len(users)):
            worksheet.write(i + 1, 0, users[i].id)
            worksheet.write(i + 1, 1, users[i].name)
            worksheet.write(i + 1, 2, users[i].stdid)
            worksheet.write(i + 1, 3, Answer.objects.filter(user=users[i]).count())

        workbook.save('JustSearch/answered_users.xls')
        self.message_user(request, "成功导出已经答题的人的数据！给我嘤！")

    reset.short_description = '重置个人'
    Promoted.short_description = '给我晋级'
    UnPromoted.short_description = '给我反晋级'
    answered.short_description = '导出数据'

    # def get_queryset(self, request):
    #     """函数作用：使当前登录的用户只能看到自己负责的服务器"""
    #     qs = super(UserDataAdmin, self).get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     return qs.filter(user=UserData.objects.filter(user_name=request.user))

    # list_display = ('machine_ip', 'application', 'colored_status', 'user', 'machine_model', 'cache',
    #                 'cpu', 'hard_disk', 'machine_os', 'idc', 'machine_group')

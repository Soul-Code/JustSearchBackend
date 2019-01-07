from django.db import models
from django.utils import timezone


# 信息系统
class UserData(models.Model):
    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    stdid = models.CharField('学号', max_length=8)
    name = models.CharField('姓名', max_length=6, null=True, blank=True)
    qq = models.CharField('QQ', max_length=12, null=True, blank=True)
    tel = models.CharField('电话', max_length=11, null=True, blank=True)

    userType = models.CharField('类型', max_length=5, null=True, blank=True)
    userDep = models.CharField('学院', max_length=16, null=True, blank=True)
    score = models.IntegerField('得分儿', default=0, null=True, blank=True)
    isPromoted = models.BooleanField('是否已晋级', default=False)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, verbose_name='所在队伍', related_name='mems', null=True,
                             blank=True)

    add_time = models.IntegerField('罚时', null=True, default=0)
    finish_time = models.FloatField('所用时长', default=0.0)
    isFinished = models.BooleanField('完成答题', default=False)

    isAlarted = models.BooleanField('提醒过吗', default=False)

    pub_time = models.DateTimeField('登入时间', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name


class TimeTable(models.Model):
    class Meta:
        verbose_name = '比赛时刻表'
        verbose_name_plural = verbose_name

    timeStart = models.DateTimeField('开始时间')
    timeEnd = models.DateTimeField('结束时间')
    name = models.CharField('比赛阶段', max_length=10)

    def __str__(self):
        return self.name


class Team(models.Model):
    class Meta:
        verbose_name = '队伍'
        verbose_name_plural = verbose_name

    name = models.CharField('队伍名称', max_length=10)
    avatar = models.ImageField('队伍头像', upload_to='team_pic/%Y%m%d/', null=True, blank=True)
    score = models.IntegerField('队伍得分', default=0, null=True, blank=True)
    leader = models.CharField('队长', max_length=6)
    add_time = models.IntegerField('罚时', null=True, default=0)
    finish_time = models.FloatField('所用时长', default=0)
    pub_time = models.DateTimeField('登入时间', auto_now_add=True, null=True, blank=True)
    isFinished = models.BooleanField('完成答题', default=False)


# 题目系统
class Question(models.Model):
    question_text = models.CharField('题目', max_length=200)
    choices = models.CharField('选项', max_length=400, default='')
    difficulty = models.IntegerField('难度', default=0)
    key = models.IntegerField('正确答案', default=0)
    stage = models.ForeignKey(to=TimeTable, on_delete=models.CASCADE, related_name='questions', verbose_name='比赛阶段',
                              null=True)

    class Meta:
        verbose_name = '题目'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    choice_text = models.CharField('选项', max_length=200)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='问题', related_name='choice')
    isRight = models.BooleanField('正确答案', default=False)

    class Meta:
        verbose_name = '选项'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.choice_text


class Answer(models.Model):
    user = models.ForeignKey('UserData', on_delete=models.CASCADE, verbose_name='答题人', related_name='answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='问题', related_name='answer')
    isRight = models.BooleanField('正确', default=False)
    choose = models.IntegerField('选项', null=True, default=None)
    pub_time = models.DateTimeField('提交时间', auto_now_add=True)
    pub_num = models.IntegerField('提交次数', default=0)
    stage = models.ForeignKey(TimeTable, on_delete=models.SET_NULL, related_name='answer', verbose_name='比赛阶段',
                              default=None, null=True)

    class Meta:
        verbose_name = '答题情况'
        verbose_name_plural = verbose_name

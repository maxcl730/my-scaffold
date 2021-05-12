
class Application(db.Model):
    meta = {
        'collection': 'applications',
        'indexes': [
            'member',
            'trial',
            {'fields': ['member', 'trial'], 'unique': True},
            'report',
            'updated_time',
            'created_time',
        ],
        'ordering': ['-created_time']
    }
    member = db.ReferenceField(Member, required=True)
    trial = db.ReferenceField(Trial, required=True)
    report = db.ReferenceField(Report)
    content = db.StringField(required=True)
    address = db.EmbeddedDocumentField(MemberAddress)
    status = db.IntField(default=0, choices=APPLICATION_STATUS)
    updated_time = db.DateTimeField(default=datetime.now())
    created_time = db.DateTimeField(default=datetime.now())

    @property
    def stage(self):
        stage = dict()
        # 用户的申请以及报告进行阶段
        # 待审批、申请失败、待发货、待提交报告、已结束
        if self.status == 0:
            # 待审批
            stage = {'report_id': '', 'number': 0, 'desc': '已结束-等待公布获奖名单'}
        elif self.status == 4:
            # 申请失败
            stage = {'report_id': '', 'number': 1, 'desc': '已结束-未获得试用'}
        elif self.status in [1, 2]:
            # 已通过申请或已发货
            if self.report is not None:
                # 已提交报告
                stage = {'report_id': self.report.id, 'number': 2, 'desc': '体验报告已完成'}
            else:
                # 未提交报告
                stage = {'report_id': '', 'number': 3, 'desc': '写体验报告'}
        return stage

    @queryset_manager
    def member_applications(doc_cls, queryset, member):
        # 返回指定会员的申请
        return queryset.filter(member=member)

    def __repr__(self):
        return "<Model Application `{}`>".format(self.trial.title + '-' + self.member.nickname)

    def __str__(self):
        return self.trial.title + '-' + self.member.nickname


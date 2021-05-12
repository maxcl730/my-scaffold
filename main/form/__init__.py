# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, TextField, TextAreaField, FileField, ValidationError, SubmitField, \
                    RadioField, BooleanField, DecimalField, IntegerField, HiddenField, FieldList, FormField, \
                    DateField, PasswordField
from wtforms_components import DateTimeField, DateRange, Email
from wtforms.validators import DataRequired, Required, Length, EqualTo
# from flask_wtf.file import FileRequired, FileAllowed
from common.helper.mapping import STATUS, RUNNING_STATUS, PUBLISH_STATUS, GOOD_STANDARD, REPORT_STATUS, PROVINCE_LIST, \
    RUNNING_STATUS_WITH_APPLICATION


class CustomForm(Form):
    class Meta(Form.Meta):
        """
        重写render_field，实现Flask-Bootstrap与render_kw的class并存
        """

        def render_field(self, field, render_kw):
            other_kw = getattr(field, 'render_kw', None)
            if other_kw is not None:
                class1 = other_kw.get('class', None)
                class2 = render_kw.get('class', None)
                if class1 and class2:
                    render_kw['class'] = class2 + ' ' + class1
                render_kw = dict(other_kw, **render_kw)
            return field.widget(field, **render_kw)


class MemberSearchForm(CustomForm):
    status = SelectField(label='状态',
                         coerce=int,
                         choices=STATUS,
                         render_kw={
                             "class": 'input-sm',
                             "style": '"width: 90px"'
                         })
    city = StringField('城市',
                       render_kw={
                           "class": 'input-sm'
                       })
    mobile = StringField('手机号',
                         render_kw={
                             "class": 'input-sm'
                         })
    nickname = StringField('昵称',
                           render_kw={
                               "class": 'input-sm'
                           })
    created_time_begin = DateTimeField('创建时间(begin)',
                                       validators=[DateRange(
                                            min=datetime(2019, 1, 1),
                                            max=datetime(2029, 12, 12)
                                       )],
                                       format='%Y-%m-%d',
                                       render_kw={
                                           "placeholder": "开始时间",
                                           "class": "input-sm",
                                           "type": "input",
                                           "autocomplete": "off",
                                       })
    created_time_end = DateTimeField('创建时间(end)',
                                     validators=[DateRange(
                                           min=datetime(2019, 1, 1),
                                           max=datetime(2029, 12, 12)
                                     )],
                                     format='%Y-%m-%d',
                                     render_kw={
                                         "placeholder": "结束时间",
                                         "class": "input-sm",
                                         "type": "input",
                                         "autocomplete": "off",
                                     })


class BlockedMemberSearchForm(CustomForm):
    nickname = StringField('昵称',
                           render_kw={
                               "class": 'input-sm'
                           })
    username = StringField('姓名',
                           render_kw={
                               "class": 'input-sm'
                           })


class InvitationSearchForm(CustomForm):
    nickname = StringField('昵称',
                           render_kw={
                               "class": 'input-sm'
                           })
    created_time_begin = DateTimeField('开始时间',
                                       validators=[DateRange(
                                            min=datetime(2019, 1, 1),
                                            max=datetime(2029, 12, 12)
                                       )],
                                       format='%Y-%m-%d',
                                       render_kw={
                                           "placeholder": "开始时间",
                                           "class": "input-sm",
                                           "type": "input",
                                           "autocomplete": "off",
                                       })
    created_time_end = DateTimeField('结束时间',
                                     validators=[DateRange(
                                           min=datetime(2019, 1, 1),
                                           max=datetime(2029, 12, 12)
                                     )],
                                     format='%Y-%m-%d',
                                     render_kw={
                                         "placeholder": "结束时间",
                                         "class": "input-sm",
                                         "type": "input",
                                         "autocomplete": "off",
                                     })


class TrialSearchForm(CustomForm):
    title = StringField('试用标题',
                        render_kw={
                            "class": 'input-sm'
                        })
    running_status = SelectField('进行状态',
                                 coerce=int,
                                 choices=RUNNING_STATUS,
                                 render_kw={
                                     "class": 'input-sm',
                                     "style": '"width: 90px"'
                                 })
    publish_status = SelectField('发布状态',
                                 coerce=int,
                                 choices=PUBLISH_STATUS,
                                 render_kw={
                                     "class": 'input-sm',
                                     "style": '"width: 90px"'
                                 })


class TrialNewForm(CustomForm):
    title = StringField(label='试用标题',
                        validators=[DataRequired(), Length(min=1, max=30)],
                        description='30个字符(中英文)',
                        render_kw={
                            "required": "1",
                            "placeholder": "输入试用标题",
                            "class": "form-control",
                            "type": "input",
                            },
                        )
    good_name = StringField(label='产品名称',
                            validators=[DataRequired(), Length(min=1, max=50)],
                            render_kw={
                                "required": "1",
                                "placeholder": "输入产品名称",
                                "class": "form-control",
                                "type": "input",
                                },
                            )
    begin_time = DateTimeField('申请时间',
                               validators=[DataRequired(),
                                           DateRange(
                                               min=datetime(2019, 1, 1),
                                               max=datetime(2029, 12, 12)
                               )],
                               render_kw={
                                   "required": "1",
                                   "placeholder": "开始时间",
                                   "class": "form-control",
                                   "type": "input",
                                   "autocomplete": "off",
                               },
                               )
    end_time = DateTimeField('结束时间',
                             validators=[DataRequired(),
                                         DateRange(
                                             min=datetime(2019, 1, 1),
                                             max=datetime(2029, 12, 12)
                             )],
                             render_kw={
                                 "required": "1",
                                 "placeholder": "结束时间",
                                 "class": "form-control",
                                 "type": "input",
                                 "autocomplete": "off",
                             },
                             )
    standard = SelectField('产品规格',
                           choices=GOOD_STANDARD,
                           coerce=int,
                           validators=[DataRequired()],
                           render_kw={
                               "required": "1",
                               "placeholder": "结束时间",
                               "class": "form-control type-id",
                               "style": "width: 100%;",
                               "data-value": "",
                               "type": "input",
                               },
                           )
    price = StringField('参考价格',
                        validators=[DataRequired()],
                        render_kw={
                             "required": "1",
                             "placeholder": "输入参考价格",
                             "class": "form-control",
                             "type": "input",
                             },
                        )
    quantity = IntegerField('试用数量',
                            validators=[DataRequired()],
                            render_kw={
                                "required": "1",
                                "placeholder": "输入使用份数",
                                "class": "form-control",
                                "type": "input",
                            },
                            )
    good_image1 = HiddenField('轮播图1',
                              render_kw={
                                  'value': '',
                                  'class': 'upload-file',
                              })
    good_image2 = HiddenField('轮播图2',
                              render_kw={
                                  'value': '',
                                  'class': 'upload-file',
                              })
    good_image3 = HiddenField('轮播图3',
                              render_kw={
                                  'value': '',
                                  'class': 'upload-file',
                              })
    description = HiddenField('产品介绍',
                              render_kw={
                                  'value': '',
                              })
    thumb_image = HiddenField('列表图',
                              render_kw={
                                  'value': '',
                                  'class': 'upload-file',
                              })
    publish_status = BooleanField('立即发布',
                                  default='checked',
                                  )
    show_list_status = BooleanField('展示申请名单',
                                    default='checked',
                                    )
    visit_num_base = IntegerField('初始人气值',
                                  render_kw={
                                      "required": "1",
                                      "class": "form-control",
                                      "type": "input",
                                  })
    submit = SubmitField('提交',
                         render_kw={
                             'class': 'btn btn-info',
                         })


class FocusForm(CustomForm):
    order = SelectField('显示顺序',
                        coerce=int,
                        validators=[DataRequired()],
                        )
    title = StringField(label='标题',
                        validators=[DataRequired(), Length(min=1, max=30)],
                        description='30汉字以内',
                        render_kw={
                            "required": "1",
                            "placeholder": "输入标题",
                            "class": "form-control",
                            "type": "input",
                            },
                        )
    image = HiddenField('焦点图',
                        render_kw={
                            'value': '',
                            'class': 'upload-file',
                        })
    submit = SubmitField('提交',
                         render_kw={
                             'class': 'btn btn-info'
                         })


class ReorderFocusForm(CustomForm):
    order = SelectField('',
                        coerce=int,
                        validators=[DataRequired()],
                        )


class AddTrialFocusForm(CustomForm):
    focus_source = RadioField('试用',
                              validators=[DataRequired()],
                              choices=[
                                    ('trial', '试用活动'),
                                    ('report', '试用报告')
                                ],
                              coerce=str,
                              default='trial',
                              )


class AddReportFocusForm(CustomForm):
    focus_source = RadioField('试用',
                              validators=[DataRequired()],
                              choices=[
                                    ('trial', '试用活动'),
                                    ('report', '试用报告')
                                ],
                              coerce=str,
                              default='report',
                              )


class BannerForm(CustomForm):
    click = StringField('链接地址',
                        description='请填写https://的网站',
                        render_kw={
                            "placeholder": "输入链接地址",
                            "class": "form-control",
                            "type": "input",
                            },
                        )
    image = HiddenField('Banner图',
                        render_kw={
                            'value': '',
                            'class': 'upload-file',
                        })
    submit = SubmitField('提交',
                         render_kw={
                             'class': 'btn btn-info'
                         })


class EditRuleForm(CustomForm):
    content = TextAreaField('规则说明',
                            validators=[Required()],
                            render_kw={
                                'class': 'form-control',
                                'rows': '15'
                            })
    submit = SubmitField('提交',
                         render_kw={
                             'class': 'btn btn-info'
                         })


class ReportSearchForm(CustomForm):
    nickname = StringField('用户昵称',
                           render_kw={
                               "class": 'input-sm',
                           })
    good_name = StringField('产品名称',
                            render_kw={
                               "class": 'input-sm',
                            })
    status = SelectField('审核状态',
                         coerce=int,
                         choices=REPORT_STATUS,
                         render_kw={
                             "class": 'input-sm',
                             "style": '"width: 90px"'
                         })

    created_time_begin = DateTimeField('开始时间',
                                       validators=[DateRange(
                                           min=datetime(2019, 1, 1),
                                           max=datetime(2029, 12, 12)
                                       )],
                                       format='%Y-%m-%d',
                                       render_kw={
                                           "placeholder": "开始时间",
                                           "class": "input-sm",
                                           "type": "input",
                                           "autocomplete": "off",
                                       })
    created_time_end = DateTimeField('结束时间',
                                     validators=[DateRange(
                                         min=datetime(2019, 1, 1),
                                         max=datetime(2029, 12, 12)
                                     )],
                                     format='%Y-%m-%d',
                                     render_kw={
                                         "placeholder": "结束时间",
                                         "class": "input-sm",
                                         "type": "input",
                                         "autocomplete": "off",
                                     })


class ApplicationSearchForm(CustomForm):
    good_name = StringField('产品名称',
                            render_kw={
                               "class": 'input-sm',
                            })
    nickname = StringField('用户昵称',
                           render_kw={
                               "class": 'input-sm',
                           })
    mobile = StringField('手机号',
                         render_kw={
                             "class": 'input-sm'
                         })
    # 试用状态
    running_status = SelectField('试用状态',
                                 coerce=int,
                                 choices=RUNNING_STATUS_WITH_APPLICATION,
                                 render_kw={
                                     "class": 'input-sm',
                                     "style": '"width: 90px"'
                                 })
    # 所在省份
    province_name = SelectField('所在省份',
                                coerce=str,
                                choices=PROVINCE_LIST,
                                render_kw={
                                     "class": 'input-sm',
                                     "style": '"width: 90px"'
                                })
    Apply_number = IntegerField('申请次数大于',
                                render_kw={
                                    "class": "input-sm",
                                    "type": "input",
                                    },
                                )
    created_time_begin = DateTimeField('开始时间',
                                       validators=[DateRange(
                                           min=datetime(2019, 1, 1),
                                           max=datetime(2029, 12, 12)
                                       )],
                                       format='%Y-%m-%d',
                                       render_kw={
                                           "placeholder": "开始时间",
                                           "class": "input-sm",
                                           "type": "input",
                                           "autocomplete": "off",
                                       })
    created_time_end = DateTimeField('结束时间',
                                     validators=[DateRange(
                                         min=datetime(2019, 1, 1),
                                         max=datetime(2029, 12, 12)
                                     )],
                                     format='%Y-%m-%d',
                                     render_kw={
                                         "placeholder": "结束时间",
                                         "class": "input-sm",
                                         "type": "input",
                                         "autocomplete": "off",
                                     })


class GoodNameForm(CustomForm):
    good_name = StringField('产品名称',
                            render_kw={
                                "class": 'input-sm',
                                "placeholder": "输入产品名称生成发货名单",
                                "required": "1",
                                "style": "width: 180px",
                            })


class UserForm(CustomForm):
    email = StringField(label='Email',
                        validators=[DataRequired(message="邮箱不能为空"), Email(message="邮箱格式不正确")],
                        description='用户使用邮箱登录管理系统',
                        render_kw={
                            "required": "1",
                            "placeholder": "输入邮箱",
                            "class": "form-control",
                            "type": "input",
                            },
                        )
    name = StringField(label='姓名',
                       validators=[DataRequired(), Length(min=1, max=30)],
                       render_kw={
                            "required": "1",
                            "placeholder": "输入姓名",
                            "class": "form-control",
                            "type": "input",
                            },
                       )
    passwd = PasswordField(label='密码',
                           validators=[DataRequired(message="密码不能为空")],
                           render_kw={
                               "required": "1",
                               "placeholder": "输入密码",
                               "class": "form-control",
                               "type": "password",
                               },
                           )
    confirm_passwd = PasswordField(label='确认密码',
                                   validators=[DataRequired(message="确认密码不能为空"), EqualTo('passwd',message="两次密码不一致")],
                                   render_kw={
                                       "required": "1",
                                       "placeholder": "再次输入密码",
                                       "class": "form-control",
                                       "type": "password",
                                       },
                           )
    submit = SubmitField('提交',
                         render_kw={
                             'class': 'btn btn-info'
                         })


class UserPasswdForm(CustomForm):
    passwd = PasswordField(label='密码',
                           validators=[DataRequired(message="密码不能为空")],
                           render_kw={
                               "required": "1",
                               "placeholder": "输入密码",
                               "class": "form-control",
                               "type": "password",
                               },
                           )
    confirm_passwd = PasswordField(label='确认密码',
                                   validators=[DataRequired(message="确认密码不能为空"), EqualTo('passwd',message="两次密码不一致")],
                                   render_kw={
                                       "required": "1",
                                       "placeholder": "再次输入密码",
                                       "class": "form-control",
                                       "type": "password",
                                       },
                           )
    submit = SubmitField('提交',
                         render_kw={
                             'class': 'btn btn-info'
                         })

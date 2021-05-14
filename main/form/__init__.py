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

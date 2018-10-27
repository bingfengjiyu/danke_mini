# coding:utf-8
import random
from datetime import datetime
import time

from flask import jsonify

from . import db



class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class Superuser(BaseModel,db.Model):
    __tablename__="dk_superuser"

    id=db.Column(db.Integer,primary_key=True)  # 用户id
    name = db.Column(db.String(32), nullable=False)  # 用户暱称
    password = db.Column(db.String(32), nullable=False)  # 密码


# 拼团用户表
class Group_user(db.Model):
    __tablename__ = "dk_group_user"

    id = db.Column(db.Integer, primary_key=True)
    group_id=db.Column(db.Integer, db.ForeignKey("dk_group_add.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("dk_user.user_id"), nullable=False)

#
# coupons_user = db.Table(
#     "dk_coupons_user",
#     db.Column("user_id",db.Integer,db.ForeignKey("dk_user.user_id"),primary_key=True),
#     db.Column("coupons_id",db.Integer,db.ForeignKey("dk_discount_coupons.id"),primary_key=True),
# )


class User(BaseModel,db.Model):
    __tablename__="dk_user"

    user_id=db.Column(db.Integer,primary_key=True)  # 用户id
    openid=db.Column(db.String(128),unique=True,nullable=False)  # 微信用户id唯一标识
    name = db.Column(db.String(32), nullable=False)  # 用户暱称
    mobile = db.Column(db.String(11), unique=True)  # 手机号
    real_name = db.Column(db.String(32))  # 真实姓名
    id_card = db.Column(db.String(20))  # 身份证号
    avatar_url = db.Column(db.String(128))  # 用户头像路径
    orders = db.relationship("OrderInfo", backref="dk_user")  # 用户下的订单
    address = db.relationship("Address", backref="dk_user")  # 用户下的订单
    group = db.relationship("Group_user", backref="dk_user")  # 用户的拼团
    comment = db.relationship("Comment", backref="dk_user")    # 我的评价
    collect = db.relationship("Goods_collect", backref="dk_user")    # 我的评价
    groupfund = db.relationship("Order_fund", backref="dk_user")    # 我的评价
    coupons = db.relationship("Coupons_user", backref="dk_user")    # 优惠券

    def __repr__(self):
        return self.name

    def get_coupons(self):
        coup_list = []
        for coup in self.coupons:
            coup_list.append(coup.id)
        return coup_list

    def to_getinfo(self):
        user_dict = {
            "user_id": self.user_id,
            "name": self.name,
            "avatar_url": self.avatar_url
        }
        return user_dict


    def to_dict(self):
        """将对象转换为字典数据"""
        user_dict = {
            "openid": self.openid,
            "user_id":self.user_id,
            "name": self.name,
            "mobile": self.mobile,
            "avatar_url": self.avatar_url
        }
        return user_dict

    # def auth_to_dict(self):
    #     """将实名信息转换为字典数据"""
    #     auth_dict = {
    #         "openid": self.openid,
    #         "real_name": self.real_name,
    #         "id_card": self.id_card
    #     }
    #     return auth_dict


class Address(BaseModel,db.Model):
    __tablename__ = "dk_address"

    id=db.Column(db.Integer,primary_key=True)
    user=db.Column(db.Integer,db.ForeignKey("dk_user.user_id"),nullable=False)
    receiver=db.Column(db.String(128),nullable=False)
    pro_city_county=db.Column(db.String(128),nullable=False)
    addr=db.Column(db.String(128),nullable=False)
    phone=db.Column(db.String(128),nullable=False)
    is_default=db.Column(
        db.Enum(
            "0",  # 默认地址
            "1",  # 不是默认地址
        ),
        default="1", index=True)  # 是否默认地址
    orders = db.relationship("OrderInfo", backref="dk_address")  # 用户下的订单

    def __repr__(self):
        return self.addr

    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        addr_dict = {
            "id": self.id,
            "receiver":self.receiver,
            "pro_city_county":self.pro_city_county,
            "addr":self.addr,
            "phone":self.phone,
            "is_default":self.is_default
        }
        return addr_dict


classify_type = db.Table(
    "dk_classify_type",
    db.Column("classify_id",db.Integer,db.ForeignKey("dk_classify.id"),primary_key=True),
    db.Column("type_id",db.Integer,db.ForeignKey("dk_goodstype.type_id"),primary_key=True),
)


classify_model = db.Table(
    "dk_classify_model",
    db.Column("classify_id",db.Integer,db.ForeignKey("dk_classify.id"),primary_key=True),
    db.Column("model_id",db.Integer,db.ForeignKey("dk_goodsmodel.id"),primary_key=True),
)


# 商品分类
class Classify(BaseModel,db.Model):
    __tablename__ = "dk_classify"

    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(128), nullable=False)  # 分类名称
    type=db.relationship("GoodsType", secondary=classify_type)
    model=db.relationship("GoodsModel", secondary=classify_model)

    def get_typelist(self):
        typelist=[]
        for t in self.type:
            typelist.append(t.to_dict())
        return typelist

    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        classify_dict = {
            "id": self.id,
            "classifyname": self.name,
            "typelist":self.get_typelist()
        }
        return classify_dict

    def __repr__(self):
        return self.name


class GoodsType(BaseModel,db.Model):
    __tablename__ = "dk_goodstype"

    type_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(128),nullable=False)   # 种类名称
    image=db.Column(db.String(128),nullable=False)  # 商品类型图片
    sku=db.relationship("GoodsSku", backref="dk_goodstype")
    classify = db.relationship("Classify", secondary=classify_type)

    def __repr__(self):
        return self.name

    def get_skulist(self):
        skulist=[]
        for s in self.sku:
            if s.is_package=="1":
                skulist.append(s.to_namedict())
        return skulist

    def get_model(self):
        data={}
        modellist=[]
        for s in self.sku:
            model=GoodsModel.query.filter(GoodsModel.id == s.model_id).first()
            modellist.append(model.to_dict())
        data["models"]=modellist
        return data

    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        imglist=[]
        for img in self.image.split(","):
            imglist.append(img)
        image=random.sample(imglist, 1)[0]
        goodstype_dict = {
            "type_id": self.type_id,
            "name": self.name,
            "image":"https://ceshi.datebook.cc:80/static"+image
        }
        return goodstype_dict


    def to_skudict(self):
        """自定义的方法，将对象转换为字典"""
        goodstype_dict = {
            "type_id": self.type_id,
            "typename": self.name,
            "is_check":"1",
            "skulist":self.get_skulist()
        }
        return goodstype_dict


class Goods(BaseModel,db.Model):
    __tablename__ = "dk_goods"

    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(128),nullable=False)  # 商品spu
    sku = db.relationship("GoodsSku", backref="dk_goods")

    def __repr__(self):
        return self.name


    def get_model(self):
        gcolors=[]
        gmodels=[]
        data={}
        for s in self.sku:
            cid=s.color_id
            mid=s.model_id
            gcolor=GoodsColor.query.filter(GoodsColor.id == cid).first()
            gmodel=GoodsModel.query.filter(GoodsModel.id == mid).first()
            gcolors.append(gcolor.to_dict())
            gmodels.append(gmodel.to_dict())

        data["colors"]=gcolors
        data["models"]=gmodels
        return data


    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        goodsSpu_dict = {
            "id": self.id,
            "name": self.name,
            "detail":self.detail,
        }
        return goodsSpu_dict


coupons_sku = db.Table(
    "dk_coupons_sku",
    db.Column("sku_id",db.Integer,db.ForeignKey("dk_goodssku.sku_id"),primary_key=True),
    db.Column("coupons_id",db.Integer,db.ForeignKey("dk_discount_coupons.id"),primary_key=True),
)



class GoodsSku(BaseModel,db.Model):
    __tablename__ = "dk_goodssku"

    sku_id=db.Column(db.Integer,primary_key=True)
    typeid=db.Column(db.Integer,db.ForeignKey("dk_goodstype.type_id"),nullable=False)    # 商品种类
    goodsid=db.Column(db.Integer,db.ForeignKey("dk_goods.id"),nullable=False)    # 商品id
    color_id = db.Column(db.Integer,db.ForeignKey("dk_goodscolor.id"),nullable=False)  # 颜色
    model_id = db.Column(db.Integer,db.ForeignKey("dk_goodsmodel.id"),nullable=False)  # 型号
    name=db.Column(db.String(256),nullable=False)
    price_unit=db.Column(db.Float(2),nullable=False) # 商品单价
    group_price=db.Column(db.Float(2)) # 拼团价格
    pnum=db.Column(db.Integer) # 商品拼团人数
    starttime = db.Column(db.DateTime)  # 商品拼团开始时间
    endtime = db.Column(db.DateTime)  # 商品拼团结束时间
    period = db.Column(db.Integer)  # 商品拼团有效时间
    package_price=db.Column(db.Float(2)) # 套餐价格
    is_package = db.Column(
        db.Enum(
            "0",  # 不是套餐
            "1",  # 是套餐
        ),
        default="0", index=True)  # 是否加入套餐
    is_check = db.Column(
        db.Enum(
            "0",  # 未选中
            "1",  # 选中
        ),
        default="0", index=True)  # 是否选中（自选套餐页面显示）
    image=db.Column(db.String(256),nullable=False) # 商品详情图片
    sku_img=db.Column(db.String(256),nullable=False) # 商品图片
    stock=db.Column(db.Integer,nullable=False) # 商品库存
    sales=db.Column(db.Integer,nullable=False)  # 商品销量
    goodsimage = db.relationship("GoodsImage", backref="dk_goodssku")
    order = db.relationship("OrderInfo", backref="dk_goodssku")
    goods_banner = db.relationship("IndexGoodsBanner", backref="dk_goodssku")
    promotion_banner = db.relationship("PromotionBanner", backref="dk_goodssku")
    coupons=db.relationship("DiscountCoupons", secondary=coupons_sku)

    def __repr__(self):
        return self.name

    def get_coupons(self):
        coup_list=[]
        for coup in self.coupons:
            coup_list.append(coup)
        return coup_list


    def to_skudict(self):
        goodsSku_dict = {
            "sku_id": self.sku_id,
            "skuname": self.name,
            "price_unit": self.price_unit,
            "sales":self.sales
        }
        return goodsSku_dict


    def to_namedict(self):
        goodsSku_dict = {
            "sku_id": self.sku_id,
            "skuname": self.name,
            "image": "https://ceshi.datebook.cc:80/static"+self.image,
            "package_price": self.package_price,
            "is_check":self.is_check    # 0：未选中商品    1：选中商品
        }

        return goodsSku_dict


    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        imglist = []
        for img in self.image.split(","):
            imglist.append("https://ceshi.datebook.cc:80/static"+img)

        goodsSku_dict = {
            "sku_id": self.sku_id,
            "typeid": self.typeid,
            "goodsid": self.goodsid,
            "color_id": self.color_id,
            "model_id": self.model_id,
            "name": self.name,
            "price_unit": self.price_unit,
            "group_price": self.group_price,
            "pnum": self.pnum,
            "starttime": self.starttime.strftime("%Y-%m-%d %H:%M:%S"),
            "endtime": self.endtime.strftime("%Y-%m-%d %H:%M:%S"),
            "package_price": self.package_price,
            "image": imglist,
            "stock": self.stock,
            "sales": self.sales,
        }

        goodsimagelist = GoodsImage.query.filter(GoodsImage.sku ==self.sku_id).all()
        imglists = []
        for goodsimage in goodsimagelist:
            imglists.append(goodsimage.to_dict().get("image"))

        goodsSku_dict["imglist"]=imglists
        return goodsSku_dict


# 商品颜色
class GoodsColor(db.Model):
    __tablename__ = "dk_goodscolor"

    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(256),nullable=False)
    sku = db.relationship("GoodsSku", backref="dk_goodscolor")

    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        goodscolor_dict = {
            "id": self.id,
            "color": self.color
        }
        return goodscolor_dict

    def __repr__(self):
        return self.color


# 商品型号
class GoodsModel(db.Model):
    __tablename__ = "dk_goodsmodel"

    id = db.Column(db.Integer, primary_key=True)
    model=db.Column(db.String(256),nullable=False)
    classify=db.relationship("Classify", secondary=classify_model)
    sku = db.relationship("GoodsSku", backref="dk_goodsmodel")

    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        goodsmodel_dict = {
            "id": self.id,
            "model": self.model
        }
        return goodsmodel_dict

    def __repr__(self):
        return str(self.model)


class GoodsImage(BaseModel,db.Model):
    __tablename__ = "dk_goods_image"

    id = db.Column(db.Integer, primary_key=True)
    sku=db.Column(db.Integer,db.ForeignKey("dk_goodssku.sku_id"),nullable=False)
    image=db.Column(db.String(258),nullable=False)

    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        goodsimage_dict = {
            "id": self.id,
            "image": "https://ceshi.datebook.cc:80/static"+self.image,
        }
        return goodsimage_dict

    def __repr__(self):
        return str(self.image)


# 轮播商品板块
class IndexGoodsBanner(BaseModel,db.Model):
    __tablename__ = "dk_goods_banner"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.Integer,db.ForeignKey("dk_goodssku.sku_id"), nullable=False)  # 商品
    image=db.Column(db.String(256),nullable=False)  # 轮播图片

    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        goodsbanner_dict = {
            "sku": self.sku,
            "image": "https://ceshi.datebook.cc:80/static"+self.image
        }
        return goodsbanner_dict

    def __repr__(self):
        return str(self.id)


# 广告板块
class PromotionBanner(BaseModel,db.Model):
    __tablename__ = "dk_promotion_banner"

    id = db.Column(db.Integer, primary_key=True)
    sku=db.Column(db.Integer,db.ForeignKey("dk_goodssku.sku_id"), nullable=False)  # 商品
    image=db.Column(db.String(256),nullable=False)

    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        promotionbanner_dict = {
            "sku": self.sku,
            "image": "https://ceshi.datebook.cc:80/static"+self.image
        }
        return promotionbanner_dict

    def __repr__(self):
        return str(self.id)


# 订单表
class OrderInfo(BaseModel, db.Model):
    __tablename__ = "dk_order_info"

    id = db.Column(db.Integer, primary_key=True)  # 订单编号
    user_id = db.Column(db.Integer, db.ForeignKey("dk_user.user_id"), nullable=False)  # 下订单的用户编号
    addr_id = db.Column(db.Integer, db.ForeignKey("dk_address.id"), nullable=False)
    sku_id = db.Column(db.Integer, db.ForeignKey("dk_goodssku.sku_id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("dk_group_add.id"))
    coupons_id = db.Column(db.Integer, db.ForeignKey("dk_discount_coupons.id"))
    total_count = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.Enum(
            "WAIT_PAYMENT",  # 待付款
            "WAIT_SHARE",  # 待分享
            "WAIT_Shipping",  # 待发货
            "WAIT_Receiving",  # 待收货
            "WAIT_COMMENT",  # 待评价
            "COMPLETE",  # 已完成
            "CANCELED",  # 已取消
        ),
        default="WAIT_PAYMENT", index=True)
    type = db.Column(
        db.Enum(
            "1",  # 单独购买
            "2",  # 发起拼团
            "3",  # 参加拼团
        ),
        default="1", index=True)  # 拼团类型
    parent = db.Column(
        db.Enum(
            "0",  # 团长
            "1",  # 团员
        ),
        default="0", index=True)  # 团长
    is_comment = db.Column(
        db.Enum(
            "0",  # 待评价
            "1",  # 已评价
        ),default="0",index=True)    # 是否评价
    trade_no = db.Column(db.String(128))  # 交易编号
    nonce_str = db.Column(db.String(128))  # 随机字符串
    comment = db.relationship("Comment", backref="dk_order_info")
    order_fund = db.relationship("Order_fund", backref="dk_order_info",uselist=False)

    def to_getgroup(self):
        userdic = {}
        userlist = []

        try:
            group=Groupadd.query.filter(Groupadd.id == self.group_id,Groupadd.status=="0").first()
        except Exception as e:
            pass

        if group:
            for u in group.user:

                user=User.query.filter(User.user_id == u.user_id).first()
                userdic["user_id"] = user.user_id
                userdic["name"] = user.name
                userdic["avatar_url"] = user.avatar_url
                userlist.append(userdic)

            groupdict = group.to_dict()
            groupdict["user"]=userlist
            return groupdict


    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        order_dict = {
            "id": self.id,
            "total_count": self.total_count,
            "total_price": self.total_price,
            "status": self.status,
            "parent": self.parent,
            "trade_no": self.trade_no,
            "coupons_id": self.coupons_id
        }
        return order_dict

    def __repr__(self):
        return str(self.id)


# 订单退款表
class Order_fund(BaseModel,db.Model):
    __tablename__ = "dk_order_fund"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("dk_user.user_id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("dk_order_info.id"), nullable=False)
    reason = db.Column(db.Text)     # 退款原因
    status = db.Column(
        db.Enum(
            "1",  # 退款中
            "2",  # 已退款
            "3",  # 退款失败
        ),index=True)  # 是否退款
    fundtime = db.Column(db.DateTime)   # 退款时间

    def __repr__(self):
        return self.status


# 评价表
class Comment(BaseModel,db.Model):
    __tablename__ = "dk_comment"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("dk_user.user_id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("dk_order_info.id"), nullable=False)
    comment = db.Column(db.Text)    # 评价内容
    images = db.Column(db.String(1024)) # 用逗号连接

    def __repr__(self):
        return self.comment


# 商品收藏表
class Goods_collect(BaseModel,db.Model):
    __tablename__ = "dk_goods_collect"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("dk_user.user_id"), nullable=False)
    status = db.Column(
        db.Enum(
            "0",  # 未收藏
            "1",  # 已收藏
        ),default="0",index=True)    # 是否收藏

    def __repr__(self):
        return self.status


# 领取优惠券表
class Coupons_user(BaseModel,db.Model):
    __tablename__ = "dk_coupons_user"

    id = db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey("dk_user.user_id"), nullable=False)
    coupons_id=db.Column(db.Integer, db.ForeignKey("dk_discount_coupons.id"), nullable=False)
    status=db.Column(
        db.Enum(
            "0",   # 已领取未使用
            "1"    # 已使用
        ),default="0",index=True)

    def is_expire(self):
        coupons = DiscountCoupons.query.filter(DiscountCoupons.id == self.coupons_id).first()
        nowtime = int(time.mktime(datetime.now().timetuple()))
        end_seconds=int(time.mktime(coupons.endtime.timetuple()))

        # 结束时间过期
        if nowtime>end_seconds:
            self.status = "-1"     # 已过期
            return False
        else:
            return True

# 优惠券
class DiscountCoupons(BaseModel,db.Model):
    __tablename__ = "dk_discount_coupons"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)    # 优惠券名称
    price=db.Column(db.Integer, nullable=False)         # 面值
    spendMoney=db.Column(db.Integer, nullable=False)    # 最低消费金额
    desc = db.Column(db.String(256))    # 使用说明
    starttime=db.Column(db.DateTime)    # 适用开始时间
    endtime=db.Column(db.DateTime)      # 适用结束时间
    stock = db.Column(db.Integer, nullable=False)       # 库存
    sku=db.relationship("GoodsSku", secondary=coupons_sku)
    order = db.relationship("OrderInfo", backref="dk_discount_coupons")
    user = db.relationship("Coupons_user", backref="dk_discount_coupons")

    def __repr__(self):
        return self.name

    def to_dict(self):
        starttime=self.starttime.strftime("%Y.%m.%d %H:%M")
        endtime=self.endtime.strftime("%Y.%m.%d %H:%M")
        # start_seconds=int(time.mktime(self.starttime.timetuple()))
        # end_seconds=int(time.mktime(self.endtime.timetuple()))
        # nowtime=int(time.mktime(datetime.now().timetuple()))
        # # 结束时间过期
        # if nowtime>end_seconds:
        #     is_expire = "1"     # 已过期
        # else:
        #     is_expire = "0"     # 未过期
        # if nowtime<start_seconds:
        #     is_start = "0"      # 未开始
        # else:
        #     is_start = "0"      # 已开始
        # print(start_seconds)
        # print(end_seconds)
        # print(nowtime)

        coupons_dict = {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "desc": self.desc,
            "starttime": starttime,
            "endtime": endtime
        }

        return coupons_dict


# 拼团参加表
class Groupadd(BaseModel,db.Model):
    __tablename__ = "dk_group_add"

    id = db.Column(db.Integer, primary_key=True)    # 拼团表id
    status = db.Column(
        db.Enum(
            "0",     # 进行中
            "1",     # 成功
            "2",     # 失败
            "3",     # 退款取消
        ),
        default="0", index=True)        # 拼团状态
    ptetime = db.Column(db.DateTime)    # 拼团结束时间
    group_num = db.Column(db.Integer)   # 拼团人数
    user = db.relationship("Group_user", backref="dk_group_add")                # 拼团的用户
    order = db.relationship("OrderInfo",backref="dk_group_add")

    def get_time(self):
        for o in self.order:
            for s in o.sku:
                print(s.starttime)


    def get_usernum(self):
        i=0
        for u in self.user:
            i+=1
        return i

    def to_dict(self):
        """自定义的方法，将对象转换为字典"""
        groupadd_dict = {
            "id": self.id,
            "ptetime": self.ptetime.strftime("%Y-%m-%d %H:%M:%S"),
            "need": self.group_num-self.get_usernum()
        }

        return groupadd_dict

    def __repr__(self):
        return str(self.id)



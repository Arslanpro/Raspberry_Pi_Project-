class Collection(object):
    @property
    def gx(self):
        return self.gx

    @gx.setter
    def gx(self, value):
        self.gx = value

    @property
    def gy(self):
        return self.gy

    @gy.setter
    def gy(self, value):
        self.gy = value

    @property
    def gz(self):
        return self.gz

    @gz.setter
    def gz(self, value):
        self.gz = value

    @property
    def ax(self):
        return self.ax

    @ax.setter
    def ax(self, value):
        self.ax = value

    @property
    def ay(self):
        return self.ay

    @ay.setter
    def ay(self, value):
        self.ay = value

    @property
    def az(self):
        return self.az

    @az.setter
    def az(self, value):
        self.az = value

    @property
    def cid(self):
        return self.cid

    @cid.setter
    def cid(self, value):
        self.cid = value

    @property
    def caid(self):
        return self.caid

    @caid.setter
    def caid(self, value):
        self.caid = value

    def __init__(self, gx, gy, gz, ax, ay, az, cid, caid):
        self.caid = caid
        self.cid = cid
        self.az = az
        self.ay = ay
        self.gz = gz
        self.gy = gy
        self.gx = gx
        self.ax = ax


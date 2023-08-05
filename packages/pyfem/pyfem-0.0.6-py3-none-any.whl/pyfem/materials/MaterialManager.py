import copy

from numpy import zeros, array


class MaterialManager(list):

    def __init__(self, matProps):
        super().__init__()

        if hasattr(matProps, 'type'):
            matType = matProps.type

            self.material = getattr(__import__('pyfem.materials.' + matType, globals(), locals(), matType, 0), matType)

            self.matlist = []
            self.matProps = matProps
            self.iSam = -1
            self.failureFlag = False

        if hasattr(matProps, 'failureType'):
            failureType = matProps.failureType

            failure = getattr(__import__('pyfem.materials.' + failureType, \
                                         globals(), locals(), failureType, 0), failureType)

            self.failure = failure(matProps)
            self.failureFlag = True

    def reset(self):

        self.iSam = -1

    def getStress(self, kinematic, iSam=-1):

        '''
        
        '''

        if iSam == -1:
            self.iSam += 1
        else:
            self.iSam = iSam

        while self.iSam >= len(self.matlist):
            self.matlist.append(self.material(self.matProps))

        self.mat = self.matlist[self.iSam]

        if self.mat.numerical_tangent:
            self.mat.store_output_flag = True
            sigma1, tang = self.mat.getStress(kinematic)

            self.mat.realNewHistory = copy.deepcopy(self.mat.new_history)

            nStr = len(kinematic.strain)

            tan0 = zeros(shape=(nStr, nStr))

            self.mat.store_output_flag = False

            for i in range(nStr):
                kin0 = copy.deepcopy(kinematic)
                kin0.strain[i] += 1.0e-9
                kin0.dstrain[i] += 1.0e-9

                sigma, tang = self.mat.getStress(kin0)

                tan0[i, :] = (sigma - sigma1) / (kin0.strain[i] - kinematic.strain[i])

            result = (sigma1, tan0)

            self.mat.new_history = copy.deepcopy(self.mat.realNewHistory)

        else:
            self.mat.store_output_flag = True
            result = self.mat.getStress(kinematic)

        if self.failureFlag:
            self.failure.check(result[0], kinematic)

        return result

    def getStressPiezo(self, kinematic, elecField, iSam=-1):

        if iSam == -1:
            self.iSam += 1
        else:
            self.iSam = iSam

        while self.iSam >= len(self.matlist):
            self.matlist.append(self.material(self.matProps))

        self.mat = self.matlist[self.iSam]

        result = self.mat.getStressPiezo(kinematic, elecField)

        if self.failureFlag:
            self.failure.check(result[0], kinematic, elecField)

        return result

    def out_labels(self):
        return self.mat.out_labels

    def outData(self):
        return self.mat.outData

    def getHistory(self, label):
        return self.mat.get_history_parameter(label)

    def commit_history(self):

        if hasattr(self, "matlist"):
            for mat in self.matlist:
                mat.commit_history()


def main():

    class Material:
        def __int__(self):
            self.type = None
            self.params = None
            self.failureType = None

    matProps = Material()
    matProps.type = "ElasticMaterial"
    matProps.params = {"E": 10.0, "nu": 0.3}
    matProps.failureType = "None"

    # 创建材料管理器对象
    matManager = MaterialManager(matProps)

    # 定义应变和电场强度
    strain = array([1.0, 0.5, 0.0])
    elecField = array([0.0, 1.0, 0.5])

    # 获取材料的应力值
    stress = matManager.getStressPiezo(kinematic=strain, elecField=elecField)

    # 打印结果
    print(f"The stress tensor is:\n{stress[0]}")
    print(f"The piezoelectric stress tensor is:\n{stress[1]}")

if __name__ == "__main__":
    main()
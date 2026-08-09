import os
from pyomo.environ import *

def define_components(mod):
    """
    定义新的模型组件（参数、变量、约束）。
    """
    # 定义一个新的参数：储能项目的能量容量上限 (MWh)
    mod.gen_storage_energy_limit_mwh = Param(
        mod.STORAGE_GENS, 
        within=NonNegativeReals, 
        default=float('inf')  # 默认无上限
    )

    # 修正后的约束规则
    def rule_storage_energy_limit(m, g, p):
        """
        确保处于活跃状态的储能项目在仿真周期内的能量容量不超过上限。
        """
        # 关键修正：检查周期 p 是否属于该发电/储能项目 g 的活跃周期 (PERIODS_FOR_GEN)
        # 这样可以安全避开 2022 年这样的历史建设年份，防止引发 KeyError
        if p not in m.PERIODS_FOR_GEN[g]:
            return Constraint.Skip
            
        return m.StorageEnergyCapacity[g, p] <= m.gen_storage_energy_limit_mwh[g]

    # 将约束的索引域改为：所有储能项目 x 所有仿真周期
    mod.Enforce_Storage_Energy_Limit = Constraint(
        mod.STORAGE_GENS, 
        mod.PERIODS, 
        rule=rule_storage_energy_limit
    )

def load_inputs(mod, switch_data, inputs_dir):
    """
    加载外部数据。
    """
    file_path = os.path.join(inputs_dir, 'storage_energy_limits.csv')
    
    if os.path.isfile(file_path):
        switch_data.load_aug(
            filename=file_path,
            param=(mod.gen_storage_energy_limit_mwh,)
        )
    else:
        print(f"提示: 未找到 {file_path}，所有储能能量容量将默认无上限。")
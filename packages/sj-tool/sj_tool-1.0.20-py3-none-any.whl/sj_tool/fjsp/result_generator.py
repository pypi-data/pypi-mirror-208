from sj_tool.fjsp.entity.fjsp_pool import FjspPool
import os
import pickle
import json


def to_gantt_json(pool: FjspPool, save_folder: str):
    gantt_data = []
    i = 0
    for machine_id in pool.machine_dict.keys():
        machine_dict = {}
        machine_object = pool.machine_dict[machine_id]
        # 放入 machine 信息
        machine_dict["id"] = machine_id
        machine_dict["rawIndex"] = i
        machine_dict["machine_name"] = machine_object.name
        i += 1
        machine_dict["machine_time"] = 0
        # 放入 operation 信息
        machine_dict["gtArray"] = []
        scheduled_op_id = machine_object.scheduled_ops
        for op_id in scheduled_op_id:
            op_object = pool.op_dict[op_id]
            machine_op_dict = {}
            machine_op_dict["process"] = pool.process_dict[op_object.process_id].name
            machine_op_dict["processId"] = op_object.process_id
            machine_op_dict["productId"] = op_object.product_id
            machine_op_dict["productSN"] = pool.product_dict[op_object.product_id].model
            machine_op_dict["count"] = pool.job_dict[op_object.job_id].demand
            machine_op_dict["start"] = op_object.op_start.strftime("%Y-%m-%d %H:%M:%S")
            machine_op_dict["end"] = op_object.op_end.strftime("%Y-%m-%d %H:%M:%S")
            machine_op_dict["Delivery"] = pool.job_dict[op_object.job_id].ots_time.strftime("%Y-%m-%d")
            machine_op_dict["operation_id"] = op_id
            machine_op_dict["job_id"] = pool.job_dict[op_object.job_id].id
            machine_op_dict["parentId"] = machine_object.id

            machine_dict["gtArray"].append(machine_op_dict)

        gantt_data.append(machine_dict)

    with open(os.path.join(save_folder, "gantt.json"), "w", encoding="utf-8") as f:
        json.dump({"data": gantt_data}, f, ensure_ascii=False)


if __name__ == "__main__":
    save_folder = "D:\shangjian\sj_tool\data"
    with open(os.path.join(save_folder, "result.pkl"), "rb") as f:
        fjsppool = pickle.load(f)

    to_gantt_json(fjsppool, save_folder)

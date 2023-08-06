from netqasm.lang.instr.core import MeasInstruction, RetRegInstruction, SetInstruction
from netqasm.lang.instr.vanilla import RotZInstruction
from netqasm.lang.operand import Register, Template
from netqasm.lang.subroutine import Subroutine

from qoala.lang.hostlang import (
    AddCValueOp,
    AssignCValueOp,
    BasicBlock,
    BasicBlockType,
    IqoalaVector,
    ReceiveCMsgOp,
    ReturnResultOp,
    RunSubroutineOp,
    SendCMsgOp,
)
from qoala.lang.program import LocalRoutine, ProgramMeta, QoalaProgram
from qoala.lang.routine import RoutineMetadata
from qoala.util.tests import text_equal


def test_serialize_meta_1():
    expected = """
META_START
name: alice
parameters: 
csockets: 0 -> bob
epr_sockets: 
META_END
    """

    meta = ProgramMeta(name="alice", parameters=[], csockets={0: "bob"}, epr_sockets={})
    assert text_equal(meta.serialize(), expected)


def test_serialize_meta_2():
    expected = """
META_START
name: alice
parameters: theta1, theta2
csockets: 0 -> bob, 1 -> charlie
epr_sockets: 1 -> charlie
META_END
    """

    meta = ProgramMeta(
        name="alice",
        parameters=["theta1", "theta2"],
        csockets={0: "bob", 1: "charlie"},
        epr_sockets={1: "charlie"},
    )
    assert text_equal(meta.serialize(), expected)


def test_serialize_host_code_1():
    expected = """
^b0 {type = CL}:
    my_value = assign_cval() : 1
    remote_id = assign_cval() : 0
    send_cmsg(remote_id, my_value)
    received_value = recv_cmsg(remote_id)
    new_value = assign_cval() : 3
    my_value = add_cval_c(new_value, new_value)
^b1 {type = QL}:
    vec<m> = run_subroutine(vec<my_value>) : subrt1
^b2 {type = CL}:
    return_result(m)
    """

    b0 = BasicBlock(
        "b0",
        BasicBlockType.CL,
        instructions=[
            AssignCValueOp("my_value", 1),
            AssignCValueOp("remote_id", 0),
            SendCMsgOp("remote_id", "my_value"),
            ReceiveCMsgOp("remote_id", "received_value"),
            AssignCValueOp("new_value", 3),
            AddCValueOp("my_value", "new_value", "new_value"),
        ],
    )
    b1 = BasicBlock(
        "b1",
        BasicBlockType.QL,
        instructions=[
            RunSubroutineOp(IqoalaVector(["m"]), IqoalaVector(["my_value"]), "subrt1"),
        ],
    )
    b2 = BasicBlock(
        "b2",
        BasicBlockType.CL,
        instructions=[
            ReturnResultOp("m"),
        ],
    )

    program = QoalaProgram(meta=ProgramMeta.empty("alice"), blocks=[b0, b1, b2])
    assert text_equal(program.serialize_host_code(), expected)


def test_serialize_subroutines_1():
    expected = """
SUBROUTINE subrt1
    params: my_value
    returns: m
    uses: 0
    keeps: 
  NETQASM_START
    set Q0 0
    rot_z Q0 {my_value} 4
    meas Q0 M0
    ret_reg M0
  NETQASM_END
    """

    Q0 = Register.from_str("Q0")
    M0 = Register.from_str("M0")
    subrt = LocalRoutine(
        name="subrt1",
        subrt=Subroutine(
            instructions=[
                SetInstruction(reg=Q0, imm=0),
                RotZInstruction(reg=Q0, imm0=Template("my_value"), imm1=4),
                MeasInstruction(reg0=Q0, reg1=M0),
                RetRegInstruction(reg=M0),
            ],
            arguments=["my_value"],
        ),
        return_vars=["m"],
        metadata=RoutineMetadata.free_all([0]),
    )
    program = QoalaProgram(
        meta=ProgramMeta.empty("alice"),
        blocks=[],
        local_routines={"subrt1": subrt},
    )
    assert text_equal(program.serialize_subroutines(), expected)


def test_serialize_subroutines_2():
    expected = """
SUBROUTINE subrt1
    params: param1
    returns: m
    uses: 0
    keeps: 
  NETQASM_START
    set R0 {param1}
    meas Q0 M0
  NETQASM_END

SUBROUTINE subrt2
    params: theta
    returns: 
    uses:
    keeps: 
  NETQASM_START
    set R0 {theta}
  NETQASM_END
    """

    R0 = Register.from_str("R0")
    Q0 = Register.from_str("Q0")
    M0 = Register.from_str("M0")
    subrt1 = LocalRoutine(
        name="subrt1",
        subrt=Subroutine(
            instructions=[
                SetInstruction(reg=R0, imm=Template("param1")),
                MeasInstruction(reg0=Q0, reg1=M0),
            ],
            arguments=["param1"],
        ),
        return_vars=["m"],
        metadata=RoutineMetadata.free_all([0]),
    )
    subrt2 = LocalRoutine(
        name="subrt2",
        subrt=Subroutine(
            instructions=[
                SetInstruction(reg=R0, imm=Template("theta")),
            ],
            arguments=["theta"],
        ),
        return_vars=[],
        metadata=RoutineMetadata.use_none(),
    )
    program = QoalaProgram(
        meta=ProgramMeta.empty("alice"),
        blocks=[],
        local_routines={"subrt1": subrt1, "subrt2": subrt2},
    )
    assert text_equal(program.serialize_subroutines(), expected)


def test_serialize_program():
    expected = """
META_START
name: alice
parameters: 
csockets: 0 -> bob
epr_sockets: 
META_END

^b0 {type = CL}:
    my_value = assign_cval() : 1
    remote_id = assign_cval() : 0
    send_cmsg(remote_id, my_value)
    received_value = recv_cmsg(remote_id)
    new_value = assign_cval() : 3
    my_value = add_cval_c(new_value, new_value)
^b1 {type = QL}:
    vec<m> = run_subroutine(vec<my_value>) : subrt1
^b2 {type = CL}:
    return_result(m)

SUBROUTINE subrt1
    params: my_value
    returns: m
    uses: 0
    keeps: 
  NETQASM_START
    set Q0 0
    rot_z Q0 {my_value} 4
    meas Q0 M0
    ret_reg M0
  NETQASM_END
    """

    meta = ProgramMeta(name="alice", parameters=[], csockets={0: "bob"}, epr_sockets={})
    b0_instructions = [
        AssignCValueOp("my_value", 1),
        AssignCValueOp("remote_id", 0),
        SendCMsgOp("remote_id", "my_value"),
        ReceiveCMsgOp("remote_id", "received_value"),
        AssignCValueOp("new_value", 3),
        AddCValueOp("my_value", "new_value", "new_value"),
    ]
    b1_instructions = [
        RunSubroutineOp(IqoalaVector(["m"]), IqoalaVector(["my_value"]), "subrt1")
    ]
    b2_instructions = [ReturnResultOp("m")]
    b0 = BasicBlock("b0", BasicBlockType.CL, b0_instructions)
    b1 = BasicBlock("b1", BasicBlockType.QL, b1_instructions)
    b2 = BasicBlock("b2", BasicBlockType.CL, b2_instructions)
    Q0 = Register.from_str("Q0")
    M0 = Register.from_str("M0")
    subrt = LocalRoutine(
        name="subrt1",
        subrt=Subroutine(
            instructions=[
                SetInstruction(reg=Q0, imm=0),
                RotZInstruction(reg=Q0, imm0=Template("my_value"), imm1=4),
                MeasInstruction(reg0=Q0, reg1=M0),
                RetRegInstruction(reg=M0),
            ],
            arguments=["my_value"],
        ),
        return_vars=["m"],
        metadata=RoutineMetadata.free_all([0]),
    )

    program = QoalaProgram(
        meta=meta, blocks=[b0, b1, b2], local_routines={"subrt1": subrt}
    )

    assert text_equal(program.serialize(), expected)


if __name__ == "__main__":
    test_serialize_meta_1()
    test_serialize_meta_2()
    test_serialize_host_code_1()
    test_serialize_subroutines_1()
    test_serialize_subroutines_2()
    test_serialize_program()

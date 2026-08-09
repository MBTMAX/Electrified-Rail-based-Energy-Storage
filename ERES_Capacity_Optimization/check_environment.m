function check_environment()
%CHECK_ENVIRONMENT Check MATLAB path and required optimization packages.

fprintf('MATLAB version: %s\n', version);

assert(exist('DEP_evaluation', 'file') == 2, ...
    'DEP_evaluation.m is not on the MATLAB path.');

assert(exist('Aggregation_model', 'file') == 2, ...
    'Aggregation_model.m is not on the MATLAB path.');

assert(exist('sdpvar', 'file') == 2, ...
    'YALMIP is not installed or not on the MATLAB path.');

assert(exist('optimize', 'file') == 2, ...
    'YALMIP optimize.m is not installed or not on the MATLAB path.');

solver_available = false;
try
    yalmip('clear');
    x = sdpvar(1);
    diagnostics = optimize([0 <= x, x <= 1], -x, ...
        sdpsettings('verbose', 0, 'solver', 'gurobi'));
    solver_available = diagnostics.problem == 0 && abs(value(x) - 1) < 1e-8;
catch
    solver_available = false;
end

assert(solver_available, ...
    'Gurobi is not available to YALMIP. Check Gurobi installation and license.');

fprintf('Environment check passed.\n');
end

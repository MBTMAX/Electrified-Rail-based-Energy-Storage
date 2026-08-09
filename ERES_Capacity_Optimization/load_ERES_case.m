function [TrainConfiguration, CaseMetadata] = load_ERES_case(caseInput)
%LOAD_ERES_CASE Load a materialized ERES case.

CaseMetadata = struct;
if ischar(caseInput) || (isstring(caseInput) && isscalar(caseInput))
    inputData = load(caseInput);
    if ~isfield(inputData, 'TrainConfiguration')
        error('load_ERES_case:MissingTrainConfiguration', ...
            'The case file must contain TrainConfiguration.');
    end
    TrainConfiguration = inputData.TrainConfiguration;
    if isfield(inputData, 'CaseMetadata')
        CaseMetadata = inputData.CaseMetadata;
    end
elseif isstruct(caseInput)
    TrainConfiguration = caseInput;
else
    error('load_ERES_case:InvalidInput', ...
        ['caseInput must be a TrainConfiguration structure or a ', ...
         'MAT-file path.']);
end

if ~isstruct(TrainConfiguration) || isempty(TrainConfiguration) || ...
        ~isrow(TrainConfiguration)
    error('load_ERES_case:InvalidTrainConfiguration', ...
        'TrainConfiguration must be a nonempty 1-by-N structure.');
end
end

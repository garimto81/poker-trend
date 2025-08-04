# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important User Requirements

**항상 한글로 말할 것.**

**항상 내가 용도 변경이나 수정을 요청하면, 먼저 해당 프로젝트 내에 포함되어 있는 md 파일을 그에 맞게 수정하고, 전체 기획서를 그에 맞게 재설계한 후 요구사항 실행할 것**

When the user requests changes or modifications:
1. First update relevant MD files within the specific project to reflect the changes
2. Redesign the entire project plan according to the changes
3. Then execute the requirements

Always communicate in Korean with the user.


## Testing Approach

**중요**: 항상 실행 테스트를 진행할 때에는 실제로 실행하여 결과물까지 정확하게 확인할 수 있는 방법을 찾아, 사용자가 요구하는 결과물과 일치하는지 확인하고, 그렇지 않으면 문제를 추론하여 해결한 후 이를 해결할 때까지 반복하여 해결한 뒤에 보고합니다.

### Testing Strategy
1. **Always run actual tests** - Don't assume code works, verify it
2. **Check output matches requirements** - Ensure results align with user expectations
3. **Debug until resolution** - If issues arise, debug iteratively until fixed
4. **Report only after verification** - Only report completion after confirming functionality
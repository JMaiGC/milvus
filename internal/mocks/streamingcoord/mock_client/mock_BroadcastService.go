// Code generated by mockery v2.46.0. DO NOT EDIT.

package mock_client

import (
	context "context"

	message "github.com/milvus-io/milvus/pkg/streaming/util/message"
	mock "github.com/stretchr/testify/mock"

	types "github.com/milvus-io/milvus/pkg/streaming/util/types"
)

// MockBroadcastService is an autogenerated mock type for the BroadcastService type
type MockBroadcastService struct {
	mock.Mock
}

type MockBroadcastService_Expecter struct {
	mock *mock.Mock
}

func (_m *MockBroadcastService) EXPECT() *MockBroadcastService_Expecter {
	return &MockBroadcastService_Expecter{mock: &_m.Mock}
}

// Broadcast provides a mock function with given fields: ctx, msg
func (_m *MockBroadcastService) Broadcast(ctx context.Context, msg message.BroadcastMutableMessage) (*types.BroadcastAppendResult, error) {
	ret := _m.Called(ctx, msg)

	if len(ret) == 0 {
		panic("no return value specified for Broadcast")
	}

	var r0 *types.BroadcastAppendResult
	var r1 error
	if rf, ok := ret.Get(0).(func(context.Context, message.BroadcastMutableMessage) (*types.BroadcastAppendResult, error)); ok {
		return rf(ctx, msg)
	}
	if rf, ok := ret.Get(0).(func(context.Context, message.BroadcastMutableMessage) *types.BroadcastAppendResult); ok {
		r0 = rf(ctx, msg)
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(*types.BroadcastAppendResult)
		}
	}

	if rf, ok := ret.Get(1).(func(context.Context, message.BroadcastMutableMessage) error); ok {
		r1 = rf(ctx, msg)
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// MockBroadcastService_Broadcast_Call is a *mock.Call that shadows Run/Return methods with type explicit version for method 'Broadcast'
type MockBroadcastService_Broadcast_Call struct {
	*mock.Call
}

// Broadcast is a helper method to define mock.On call
//   - ctx context.Context
//   - msg message.BroadcastMutableMessage
func (_e *MockBroadcastService_Expecter) Broadcast(ctx interface{}, msg interface{}) *MockBroadcastService_Broadcast_Call {
	return &MockBroadcastService_Broadcast_Call{Call: _e.mock.On("Broadcast", ctx, msg)}
}

func (_c *MockBroadcastService_Broadcast_Call) Run(run func(ctx context.Context, msg message.BroadcastMutableMessage)) *MockBroadcastService_Broadcast_Call {
	_c.Call.Run(func(args mock.Arguments) {
		run(args[0].(context.Context), args[1].(message.BroadcastMutableMessage))
	})
	return _c
}

func (_c *MockBroadcastService_Broadcast_Call) Return(_a0 *types.BroadcastAppendResult, _a1 error) *MockBroadcastService_Broadcast_Call {
	_c.Call.Return(_a0, _a1)
	return _c
}

func (_c *MockBroadcastService_Broadcast_Call) RunAndReturn(run func(context.Context, message.BroadcastMutableMessage) (*types.BroadcastAppendResult, error)) *MockBroadcastService_Broadcast_Call {
	_c.Call.Return(run)
	return _c
}

// NewMockBroadcastService creates a new instance of MockBroadcastService. It also registers a testing interface on the mock and a cleanup function to assert the mocks expectations.
// The first argument is typically a *testing.T value.
func NewMockBroadcastService(t interface {
	mock.TestingT
	Cleanup(func())
}) *MockBroadcastService {
	mock := &MockBroadcastService{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}